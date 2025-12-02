#!/usr/bin/env python3
"""
🗺️ GERADOR AUTOMÁTICO DE MAPAS ISOTÓPICOS - VERSÃO STANDALONE

Arquivo único e independente que integra todas as funcionalidades necessárias:
• Conexão com Firebase (opcional)
• Processamento geoespacial com rasterio e geopandas  
• Geração de mapas de probabilidade isotópica com z-test estatístico
• Aplicação de máscaras do Brasil
• Criação automática de PDFs com visualizações categorizadas
• Modo de teste sem dependências externas

FUNCIONALIDADES INTEGRADAS:
✅ generate_new_mapa.py : Algoritmos de probabilidade estatística (z-test)
✅ Firebase integration : Busca automática de documentos isotópicos
✅ Shapefile handling  : Detecção automática de contornos do Brasil
✅ Error recovery      : Fallbacks para modo offline/teste
✅ CLI interface       : Parâmetros da linha de comando
✅ Auto PDF generation : Abertura automática de resultados
✅ Color-coded maps    : Verde ≥95%, Amarelo 5-95%, Vermelho <5%

ALGORITMO: Usa z-test bilateral para calcular probabilidade (0-100%) de que cada 
pixel seja a origem da amostra. Valores altos (verde) indicam compatibilidade 
estatística, valores baixos (vermelho) indicam incompatibilidade.

USO: python create_mapa_local.py [DOC_ID] [O18_VALUE]
"""

import sys
import os
import pandas as pd
from datetime import datetime
import warnings
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import reproject, Resampling
from scipy.stats import norm, multivariate_normal
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from typing import Optional, Union, Literal
from pathlib import Path

# ============================================================================
# FUNCIONALIDADES INTEGRADAS DO generate_new_mapa.py
# ============================================================================

def compare_geom(r1_profile, r2_profile):
    """Compares the geometry of two rasterio profiles."""
    if r1_profile['crs'] != r2_profile['crs']:
        raise ValueError("Rasters have different CRS.")
    
    # Use tolerance for transform comparison to avoid floating point precision issues
    t1 = r1_profile['transform']
    t2 = r2_profile['transform']
    if not np.allclose([t1.a, t1.b, t1.c, t1.d, t1.e, t1.f], 
                       [t2.a, t2.b, t2.c, t2.d, t2.e, t2.f], 
                       rtol=1e-6):
        raise ValueError("Rasters have different transform (georeferencing).")
    
    if r1_profile['height'] != r2_profile['height'] or r1_profile['width'] != r2_profile['width']:
        raise ValueError("Rasters have different dimensions.")
    return True

def process_ref_trans(unknown):
    """Processes a dictionary simulating an R 'refTrans' object."""
    if not isinstance(unknown, dict) or 'data' not in unknown:
        raise TypeError("Only dictionary-based 'refTrans' objects can be provided in a list.")

    df = unknown['data']
    if df.shape[1] == 3:
        # Assuming columns are [value, err, stationID] and we need to add sample IDs
        un = pd.DataFrame({
            'ID': range(1, len(df) + 1),
            df.columns[0]: df.iloc[:, 0]
        })
        print("Info: No sample IDs in refTrans object, assigning numeric sequence.")
    elif df.shape[1] == 4:
        # Assuming columns are [ID, value, err, stationID]
        un = df.iloc[:, 0:2]
    else:
        raise ValueError("Incorrectly formatted refTrans object in unknown")

    return un

def check_unknown(unknown, n_isoscapes):
    """Validates the unknown samples DataFrame."""
    if isinstance(unknown, dict) and 'data' in unknown: # A single refTrans object
        unknown = process_ref_trans(unknown)

    if isinstance(unknown, list):
        if len(unknown) < n_isoscapes:
            raise ValueError("Number of refTrans objects provided is less than number of isoscapes.")
        if len(unknown) > n_isoscapes:
            warnings.warn(f"More refTrans objects than isoscapes, only using first {n_isoscapes} objects.")

        # Process and merge multiple refTrans objects
        un = process_ref_trans(unknown[0])
        nobs = len(un)
        for i in range(1, n_isoscapes):
            u = process_ref_trans(unknown[i])
            if len(u) != nobs:
                raise ValueError("Different numbers of samples in refTrans objects.")
            un = pd.merge(un, u, on='ID', how='inner')
            if len(un) != nobs:
                raise ValueError("Sample IDs in refTrans objects don't match, resulting in lost samples.")
        unknown = un

    if not isinstance(unknown, pd.DataFrame):
        raise TypeError("unknown should be a pandas DataFrame.")

    if unknown.shape[1] < (n_isoscapes + 1):
        raise ValueError("unknown must contain sample ID in column 0 and isotope values in subsequent columns.")

    if unknown.shape[1] > (n_isoscapes + 1):
        warnings.warn(f"More than {n_isoscapes + 1} columns in unknown; assuming IDs in col 0 and values in cols 1 to {n_isoscapes + 1}.")
        unknown = unknown.iloc[:, :(n_isoscapes + 1)]

    return unknown

def check_mask(mask, base_profile):
    """Validates and processes the mask parameter."""
    if mask is None:
        return None
    
    # Permitir tanto caminho de arquivo (string) quanto GeoDataFrame já em memória
    if isinstance(mask, gpd.GeoDataFrame):
        mask_gdf = mask
        if mask_gdf.crs != base_profile['crs']:
            mask_gdf = mask_gdf.to_crs(base_profile['crs'])
        return mask_gdf

    if not isinstance(mask, str):
        raise TypeError("mask should be a string path to a vector file or a GeoDataFrame.")
    
    if not os.path.exists(mask):
        raise FileNotFoundError(f"Mask file not found: {mask}")
    
    try:
        # Read the mask shapefile and reproject to raster CRS if needed
        mask_gdf = gpd.read_file(mask)
        if mask_gdf.crs != base_profile['crs']:
            mask_gdf = mask_gdf.to_crs(base_profile['crs'])
        return mask_gdf
    except Exception as e:
        raise ValueError(f"Error reading mask file: {e}")

def check_options(genplot, out_dir):
    """Validates plotting and output directory options."""
    if not isinstance(genplot, bool):
        raise TypeError("genplot must be boolean (True or False)")
    
    if genplot and out_dir is None:
        warnings.warn("genplot is True but no out_dir specified. Plots will not be saved.")
    
    if out_dir is not None:
        out_dir = Path(out_dir)
        if not out_dir.exists():
            print(f"Creating output directory: {out_dir}")
            out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir
    return None


def build_local_mask_from_point(
    lat: float,
    lon: float,
    area_km2: float,
    base_profile: dict,
) -> Optional[gpd.GeoDataFrame]:
    """Cria um buffer circular em torno de (lat, lon) com área aproximada em km².

    Aproximação: assume 1 grau de latitude ≈ 111 km e ajusta longitude por cos(lat).
    O raio r (em km) para uma área A é r = sqrt(A / π). Converte r para graus
    e cria um polígono (buffer) no CRS do raster.
    
    Args:
        lat: Latitude do ponto central em graus decimais.
        lon: Longitude do ponto central em graus decimais.
        area_km2: Área desejada em km².
        base_profile: Profile do raster base (para obter CRS).
    
    Returns:
        GeoDataFrame com o polígono circular ou None se parâmetros inválidos.
        
    Raises:
        TypeError: Se area_km2 não for numérico.
        ValueError: Se lat/lon/area_km2 estiverem fora de intervalos válidos.
    """
    if lat is None or lon is None or area_km2 is None:
        return None

    # Validações rigorosas com exceções específicas
    try:
        area_km2 = float(area_km2)
    except (TypeError, ValueError) as e:
        raise TypeError(f"area_km2 must be numeric, got {type(area_km2).__name__}: {e}")
    
    if not -90 <= lat <= 90:
        raise ValueError(f"lat must be between -90 and 90, got {lat}")
    if not -180 <= lon <= 180:
        raise ValueError(f"lon must be between -180 and 180, got {lon}")
    if area_km2 <= 0:
        raise ValueError(f"area_km2 must be positive, got {area_km2}")

    # Raio em km a partir da área A = π r²
    radius_km = np.sqrt(area_km2 / np.pi)

    # Converter raio em graus (aproximação)
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * np.cos(np.radians(lat))
    if km_per_deg_lon == 0:
        km_per_deg_lon = 1e-6

    radius_deg_lat = radius_km / km_per_deg_lat
    radius_deg_lon = radius_km / km_per_deg_lon

    # Usar média dos dois para um buffer aproximado em graus
    radius_deg = float(np.mean([radius_deg_lat, radius_deg_lon]))

    # Criar ponto em WGS84
    point_wgs84 = gpd.GeoDataFrame(
        geometry=[Point(lon, lat)],
        crs="EPSG:4326",
    )

    # Reprojetar para CRS do raster, fazer buffer em unidades de grau/metro conforme CRS
    raster_crs = base_profile.get("crs")
    if raster_crs is None:
        warnings.warn("Raster sem CRS definido; não é possível criar recorte local.")
        return None

    point_in_crs = point_wgs84.to_crs(raster_crs)

    # Heurística: se CRS é geográfico (EPSG:4326), buffer em graus; se projetado, em km*1000
    is_geographic = str(raster_crs).upper().startswith("EPSG:4326") or "GEOGCS" in str(raster_crs)

    if is_geographic:
        local_buffer = point_in_crs.buffer(radius_deg)
    else:
        local_buffer = point_in_crs.buffer(radius_km * 1000.0)

    local_mask = gpd.GeoDataFrame(geometry=local_buffer, crs=point_in_crs.crs)
    return local_mask

def _pd_raster_default(r, data, prior, mask_gdf, genplot, out_dir):
    """Implementation for single isoscape mode using statistical z-test."""
    print("Processing single isoscape...")
    
    # Read the isoscape raster (2-band: mean, sd)
    with rasterio.open(r) as src:
        if src.count != 2:
            raise ValueError("Raster must have exactly 2 bands (mean, standard deviation).")
        
        mean_band = src.read(1).astype(np.float64)
        sd_band = src.read(2).astype(np.float64)
        profile = src.profile
        transform = src.transform
        
        # Apply mask if provided
        if mask_gdf is not None:
            shapes = [geom for geom in mask_gdf.geometry]
            mean_masked, transform_masked = rio_mask(src, shapes, crop=True, indexes=1)
            sd_masked, _ = rio_mask(src, shapes, crop=True, indexes=2)
            
            # Extract array from masked result - handle both single and multi-band cases
            if isinstance(mean_masked, np.ma.MaskedArray):
                mean_band = mean_masked.filled(np.nan).astype(np.float64)
                sd_band = sd_masked.filled(np.nan).astype(np.float64)
            else:
                # Handle array returned from rio_mask - could be 2D or 3D
                if mean_masked.ndim == 3:
                    mean_band = mean_masked[0].astype(np.float64)
                    sd_band = sd_masked[0].astype(np.float64)
                else:
                    mean_band = mean_masked.astype(np.float64)
                    sd_band = sd_masked.astype(np.float64)
            
            # Update profile for masked raster
            profile.update({
                'height': mean_band.shape[0],
                'width': mean_band.shape[1],
                'transform': transform_masked
            })
            transform = transform_masked
    
    # Process prior if provided
    prior_band = None
    if prior is not None:
        with rasterio.open(prior) as prior_src:
            if prior_src.count != 1:
                raise ValueError("Prior raster must have exactly 1 band.")
            
            # Check geometry compatibility
            compare_geom(profile, prior_src.profile)
            prior_band = prior_src.read(1).astype(np.float64)
            
            # Apply same mask to prior
            if mask_gdf is not None:
                shapes = [geom for geom in mask_gdf.geometry]
                prior_masked, _ = rio_mask(prior_src, shapes, crop=True, indexes=1)
                
                # Handle masked array properly
                if isinstance(prior_masked, np.ma.MaskedArray):
                    prior_band = prior_masked.filled(np.nan).astype(np.float64)
                else:
                    if prior_masked.ndim == 3:
                        prior_band = prior_masked[0].astype(np.float64)
                    else:
                        prior_band = prior_masked.astype(np.float64)
    
    # Calculate probability for each unknown sample
    results = []
    
    for idx, row in data.iterrows():
        sample_id = row.iloc[0]
        sample_value = row.iloc[1]
        
        print(f"Processing sample {sample_id}: δ18O = {sample_value}")
        
        # Create masks for valid data
        valid_mask = ~(np.isnan(mean_band) | np.isnan(sd_band) | (sd_band <= 0))
        
        # Calculate probability using statistical z-test (not normalized density)
        prob_surface = np.full_like(mean_band, np.nan, dtype=np.float64)
        
        # Only calculate where we have valid data
        valid_indices = np.where(valid_mask)
        if len(valid_indices[0]) > 0:
            mean_vals = mean_band[valid_indices]
            sd_vals = sd_band[valid_indices]
            
            # Calculate probability using two-tailed z-test
            # For each pixel, calculate how many standard deviations away the sample is
            z_scores = np.abs((sample_value - mean_vals) / sd_vals)
            
            # Convert z-score to probability (two-tailed test)
            # p-value = probability that the sample COULD come from this pixel
            # Use survival function (1 - CDF) for two-tailed test
            p_values = 2 * norm.sf(z_scores)  # sf = 1 - cdf (survival function)
            
            # Convert to percentage (0-100)
            prob_percentage = p_values * 100
            
            prob_surface[valid_indices] = prob_percentage
        
        # Apply prior if available
        if prior_band is not None:
            prior_valid = ~np.isnan(prior_band)
            combined_valid = valid_mask & prior_valid
            prob_surface[combined_valid] *= prior_band[combined_valid]
        
        results.append(prob_surface)
        
        # Save individual raster if output directory specified
        if out_dir is not None:
            out_dir_path = Path(out_dir) if isinstance(out_dir, str) else out_dir
            output_path = out_dir_path / f"prob_{sample_id}.tif"
            
            # Update profile for output
            out_profile = profile.copy()
            out_profile.update({
                'dtype': 'float64',
                'count': 1,
                'compress': 'lzw'
            })
            
            with rasterio.open(str(output_path), 'w', **out_profile) as dst:
                dst.write(prob_surface, 1)
                dst.set_band_description(1, 'Probability (%) - Two-tailed z-test')
            
            print(f"Saved probability raster: {output_path}")
    
    # Generate plots if requested
    if genplot and out_dir is not None:
        _generate_plots(results, data, profile, transform, out_dir, mask_gdf)
    
    return results

def _generate_plots(results, data, profile, transform, out_dir, mask_gdf=None):
    """Generate PDF plots for probability surfaces with categorical color coding.

    Melhora a leitura geográfica adicionando:
    - contorno dos estados do Brasil (IBGE ADM1), quando disponível
    - contorno forte da máscara (Brasil / recorte local) como fronteira
    """
    from matplotlib.colors import ListedColormap, BoundaryNorm
    
    out_dir_path = Path(out_dir) if isinstance(out_dir, str) else out_dir
    pdf_path = out_dir_path / "output_pdRaster.pdf"
    
    with PdfPages(pdf_path) as pdf:
        for i, (prob_surface, (_, row)) in enumerate(zip(results, data.iterrows())):
            sample_id = row.iloc[0]
            sample_value = row.iloc[1]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create extent for proper georeferencing
            height, width = prob_surface.shape
            left = transform.c
            right = transform.c + width * transform.a
            bottom = transform.f + height * transform.e
            top = transform.f
            extent = [left, right, bottom, top]
            
            # Categorical colormap: Green (≥95%), Yellow (5-95%), Red (<5%)
            colors = ['#d73027', '#fee08b', '#1a9850']  # Red, Yellow, Green
            cmap = ListedColormap(colors)
            bounds = [0, 5, 95, 100]
            norm = BoundaryNorm(bounds, cmap.N)
            
            # Mask NaN values for visualization
            prob_masked = np.ma.masked_where(np.isnan(prob_surface), prob_surface)
            
            # Plot probability surface
            im = ax.imshow(prob_masked, extent=extent, cmap=cmap, norm=norm,
                          aspect='auto', origin='upper', interpolation='nearest')

            # --- AUTO-ZOOM: ajustar limites do eixo para mostrar só a área analisada ---
            if mask_gdf is not None and not mask_gdf.empty:
                try:
                    bounds = mask_gdf.total_bounds  # [minx, miny, maxx, maxy]
                    margin = 0.02  # 2% de margem extra ao redor
                    width = bounds[2] - bounds[0]
                    height = bounds[3] - bounds[1]
                    ax.set_xlim(bounds[0] - margin * width, bounds[2] + margin * width)
                    ax.set_ylim(bounds[1] - margin * height, bounds[3] + margin * height)
                except Exception as e:
                    print(f"⚠️  Não foi possível fazer zoom automático: {e}")

            # --- Camada 1: contorno dos estados do Brasil (IBGE ADM1), se disponível ---
            try:
                adm1_path = 'shapefiles/bra_admbnda_adm1_ibge_2020.shp'
                if os.path.exists(adm1_path):
                    estados_gdf = gpd.read_file(adm1_path)
                    # Se não tiver CRS definido, assumir WGS84
                    if estados_gdf.crs is None:
                        estados_gdf.set_crs("EPSG:4326", inplace=True)
                    if estados_gdf.crs != profile['crs']:
                        estados_gdf = estados_gdf.to_crs(profile['crs'])
                    estados_gdf.boundary.plot(ax=ax, color='#999999', linewidth=0.6, alpha=0.8)
            except Exception as e:
                print(f"⚠️  Não foi possível desenhar estados do Brasil: {e}")

            # --- Camada 2: máscara Brasil/local (fronteira do mapa analisado) ---
            if mask_gdf is not None:
                try:
                    # Linha mais espessa para indicar borda da área analisada (Brasil / recorte)
                    mask_gdf.boundary.plot(ax=ax, color='black', linewidth=1.5, alpha=1.0)
                except Exception as e:
                    print(f"⚠️  Não foi possível desenhar contorno da máscara: {e}")
            
            # Add colorbar with custom labels
            cbar = plt.colorbar(im, ax=ax, shrink=0.8, boundaries=bounds, ticks=[2.5, 50, 97.5])
            cbar.ax.set_yticklabels(['<5%\n(Low)', '5-95%\n(Medium)', '≥95%\n(High)'])
            cbar.set_label('Probability (%)', rotation=270, labelpad=20)
            
            # Set labels and title
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title(
                f'Brazil – Local Origin Probability (O-18)\n'
                f'Sample {sample_id}  |  δ18O = {sample_value:.2f}‰\n'
                f'(Two-tailed z-test, area outside border = fora do Brasil / sem dado)'
            )
            
            # Add grid
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    
    print(f"PDF saved to: {pdf_path}")

def pd_raster(
    r: Union[str, Path],
    unknown: pd.DataFrame,
    prior: Optional[Union[str, Path]] = None,
    mask: Optional[Union[str, Path, gpd.GeoDataFrame]] = None,
    genplot: bool = True,
    out_dir: Optional[Union[str, Path]] = None,
) -> list:
    """
    Calculates statistical probability of origin for unknown samples based on isoscapes.
    
    Uses two-tailed z-test to determine the probability (0-100%) that each pixel 
    could be the origin of the sample. Unlike normalized density (sum=1.0), each 
    pixel's probability is independent and represents statistical compatibility.
    
    Color coding:
    - Green (≥95%): High probability - statistically compatible
    - Yellow (5-95%): Medium probability - possible but uncertain
    - Red (<5%): Low probability - statistically incompatible
    
    Args:
        r: Path to a 2-band (mean, sd) GeoTIFF for isoscape.
        unknown: DataFrame with sample data (ID, value).
        prior: Path to prior probabilities raster. Defaults to None.
        mask: Path to polygon shapefile or GeoDataFrame for masking. Defaults to None.
        genplot: Generate plots. Defaults to True.
        out_dir: Output directory. Defaults to None.
    
    Returns:
        List of probability surfaces (0-100%) for each sample.
        
    Raises:
        TypeError: If r is not a string or Path.
        ValueError: If unknown DataFrame is invalid.
    """
    # Validações rigorosas
    if not isinstance(r, (str, Path)):
        raise TypeError("r must be a string path or Path object")
    
    if not isinstance(unknown, pd.DataFrame):
        raise TypeError("unknown must be a pandas DataFrame")
    
    # Validate options first
    out_dir = check_options(genplot, out_dir)
    
    if isinstance(r, (str, Path)):
        print("Running in single-isoscape mode.")
        n_isoscapes = 1
        data = check_unknown(unknown, n_isoscapes)
        
        # Cache profile to avoid redundant file read
        with rasterio.open(r) as src:
            base_profile = src.profile
        mask_gdf = check_mask(mask, base_profile)
        return _pd_raster_default(r, data, prior, mask_gdf, genplot, out_dir)
    else:
        raise TypeError("Argument 'r' must be a string (filepath).")

def get_firebase_client():
    """Conecta com Firebase usando credenciais locais"""
    credenciais_paths = [
        "serviceAccountKey.json",
        "../serviceAccountKey.json",
    ]
    
    credencial_encontrada = None
    for path in credenciais_paths:
        if os.path.exists(path):
            credencial_encontrada = path
            break
    
    if not credencial_encontrada:
        print("❌ ERRO: Nenhum arquivo de credenciais Firebase encontrado!")
        print("📁 Caminhos procurados:")
        for path in credenciais_paths:
            print(f"   • {path}")
        print("\n💡 Solução:")
        print("   1. Obtenha serviceAccountKey.json do Firebase Console")
        print("   2. Coloque em fraud-detection-generate-maps/serviceAccountKey.json")
        return None
    
    print(f"✅ Encontrou credenciais: {credencial_encontrada}")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credencial_encontrada
    
    from google.cloud import firestore
    db = firestore.Client()
    print("✅ Conectado ao Firebase")
    return db

def buscar_documento(db, doc_id):
    """Busca documento em todas as coleções possíveis"""
    colecoes = ['trusted_samples', 'untrusted_samples', 'unknown_samples']
    
    print(f"\n🔍 Buscando documento: {doc_id}")
    
    for colecao in colecoes:
        try:
            doc_ref = db.collection(colecao).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_data = doc.to_dict()
                print(f"✅ Documento encontrado na coleção: {colecao}")
                
                lat = doc_data.get('lat') or doc_data.get('latitude')
                lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude')
                
                # Extrair valores isotópicos - PRIORIZAR campo 'isotopes' se existir
                isotopes = {}
                
                # Primeiro tentar buscar do campo 'isotopes' (estruturado)
                if 'isotopes' in doc_data and isinstance(doc_data['isotopes'], dict):
                    isotopes.update(doc_data['isotopes'])
                    print(f"🧪 Isótopos do campo 'isotopes': {isotopes}")
                
                # Depois buscar campos diretos (fallback) - mas SEM sobrescrever
                isotope_fields = ['O18', 'C13', 'N15', 'H2', 'S34', 
                                 'd18O', 'd13C', 'd15N', 'd2H', 'd34S',
                                 'oxygen_18', 'carbon_13', 'nitrogen_15']
                
                for field in isotope_fields:
                    if field in doc_data and field not in isotopes:
                        isotopes[field] = doc_data[field]
                
                print(f"📍 Coordenadas: ({lat}, {lon})")
                print(f"🧪 Isótopos finais: {list(isotopes.keys())}")
                print(f"📊 Valores: {isotopes}")
                
                return {
                    'id': doc_id,
                    'lat': float(lat) if lat else None,
                    'lon': float(lon) if lon else None,
                    'isotopes': isotopes,
                    'org_name': doc_data.get('org_name', 'N/A'),
                    'colecao': colecao,
                    'raw_data': doc_data  # Incluir dados completos para debug
                }
        except Exception as e:
            continue
    
    return None

def create_test_data():
    """Cria dados de teste quando Firebase não estiver disponível."""
    return {
        'id': 'test_sample_001',
        'lat': -13.0845,
        'lon': -53.3795,
        'isotopes': {'O18': 23.5},
        'org_name': 'Teste',
        'colecao': 'test_data',
        'raw_data': {'d18O_cel': [23, 24]}
    }

def print_help():
    """Imprime informações de uso do script."""
    print("""
🗺️  GERADOR AUTOMÁTICO DE MAPAS ISOTÓPICOS - VERSÃO STANDALONE

USO:
  python run_generate_mapa_auto.py [DOC_ID] [O18_VALUE]

PARÂMETROS:
  DOC_ID     : ID do documento no Firebase (opcional, padrão: 6ed0ffa36587c49f5b54)
  O18_VALUE  : Valor δ18O em ‰ (opcional, busca no Firebase se não fornecido)

EXEMPLOS:
  python run_generate_mapa_auto.py                           # Usar documento padrão
  python run_generate_mapa_auto.py abc123def456              # Usar documento específico
  python run_generate_mapa_auto.py abc123def456 -12.5       # Usar documento e valor específicos
  python run_generate_mapa_auto.py test_sample -15.2        # Modo teste com valor manual

ARQUIVOS NECESSÁRIOS:
  • isoscapes/oxygen_18_detailed.tiff        : Isoscape Oxigênio-18 (1024x1024, ~4.3km/pixel)
  • shapefiles/bra_admbnda_adm0_ibge_2020.shp : Contorno do Brasil (opcional)
  • ../serviceAccountKey.json                : Credenciais Firebase (opcional)

SAÍDA:
  • output_maps/[DOC_ID]_[TIMESTAMP]/prob_[DOC_ID].tif : Raster de probabilidade (0-100%)
  • output_maps/[DOC_ID]_[TIMESTAMP]/output_pdRaster.pdf : Mapa em PDF com cores categóricas
  
INTERPRETAÇÃO:
  • Verde (≥95%): Origem altamente provável (estatisticamente compatível)
  • Amarelo (5-95%): Origem possível (incerteza moderada)
  • Vermelho (<5%): Origem improvável (estatisticamente incompatível)
""")

def main():
    # Aceitar parâmetros da linha de comando
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        return
    
    if len(sys.argv) > 1:
        doc_id = sys.argv[1]
    else:
        doc_id = "6ed0ffa36587c49f5b54"  # ID padrão
    
    # Valor isotópico opcional
    override_o18 = None
    # Área opcional (km²) para recorte local em torno da amostra
    override_area_km2 = None
    if len(sys.argv) > 2:
        try:
            override_o18 = float(sys.argv[2])
            print(f"🧪 Usando valor δ18O fornecido: {override_o18}‰")
        except ValueError:
            print(f"⚠️  Valor δ18O inválido: {sys.argv[2]}")
    if len(sys.argv) > 3:
        try:
            override_area_km2 = float(sys.argv[3])
            if override_area_km2 > 10000:
                print(f"📏 Área solicitada ({override_area_km2} km²) > 10.000 km² → usando Brasil inteiro (sem recorte local)")
                override_area_km2 = None
            else:
                print(f"📏 Usando área local fornecida: {override_area_km2} km²")
        except ValueError:
            print(f"⚠️  Área inválida (km²): {sys.argv[3]}")
    
    print(f"📋 Usando documento ID: {doc_id}")
    
    print("=" * 70)
    print("🗺️  GERADOR AUTOMÁTICO DE MAPAS ISOTÓPICOS - VERSÃO STANDALONE")
    print("=" * 70)
    
    # 1. Conectar ao Firebase (OBRIGATÓRIO)
    db = get_firebase_client()
    if not db:
        print("\n❌ ERRO: Não foi possível conectar ao Firebase")
        print("💡 Sistema requer conexão com Firebase para buscar dados das amostras")
        return
    
    # 2. Buscar documento (OBRIGATÓRIO)
    doc_data = buscar_documento(db, doc_id)
    if not doc_data:
        print(f"\n❌ ERRO: Documento '{doc_id}' não encontrado no Firebase!")
        print("📁 Coleções verificadas:")
        print("   • trusted_samples")
        print("   • untrusted_samples")
        print("   • unknown_samples")
        print("\n💡 Solução:")
        print(f"   1. Verifique se o ID '{doc_id}' está correto")
        print("   2. Confirme que o documento existe em alguma coleção")
        print("   3. Use: python create_mapa_local.py [DOC_ID_CORRETO]")
        return
    
    # 3. Extrair valor δ18O (OBRIGATÓRIO - d18O_cel apenas)
    o18_value = None
    
    if override_o18 is not None:
        # Valor fornecido via linha de comando tem prioridade
        o18_value = override_o18
        print(f"\n🎯 Usando valor δ18O da linha de comando: {o18_value}‰")
    else:
        # Buscar APENAS d18O_cel (campo padrão do sistema)
        if 'd18O_cel' not in doc_data['raw_data']:
            print(f"\n❌ ERRO: Campo 'd18O_cel' não encontrado no documento!")
            print("📊 Campos disponíveis no documento:")
            for key in sorted(doc_data['raw_data'].keys()):
                print(f"   • {key}")
            print("\n💡 Solução:")
            print("   1. Adicione o campo 'd18O_cel' ao documento no Firestore")
            print("   2. Ou forneça valor manualmente: python create_mapa_local.py DOC_ID VALOR_O18")
            print(f"   3. Exemplo: python create_mapa_local.py {doc_id} 26.5")
            return
        
        d18o_cel = doc_data['raw_data']['d18O_cel']
        print(f"\n📊 Encontrado d18O_cel: {d18o_cel}")
        
        # Validar tipo e valores
        if isinstance(d18o_cel, list):
            # Filtrar valores válidos (não NaN, não None)
            valid_values = [v for v in d18o_cel if not (isinstance(v, float) and np.isnan(v)) and v is not None]
            
            if len(valid_values) < 2:
                print(f"\n❌ ERRO: d18O_cel tem valores insuficientes!")
                print(f"📊 Valores encontrados: {d18o_cel}")
                print(f"📊 Valores válidos: {valid_values}")
                print(f"📊 Necessário: pelo menos 2 valores válidos para calcular média")
                print("\n💡 Solução:")
                print("   1. Adicione mais medições de δ18O ao campo 'd18O_cel'")
                print("   2. Ou forneça valor manualmente: python create_mapa_local.py DOC_ID VALOR_O18")
                return
            
            o18_value = np.mean(valid_values)
            print(f"✅ Calculando MÉDIA de {len(valid_values)} valores: {o18_value:.2f}‰")
            
        elif d18o_cel is not None and not (isinstance(d18o_cel, float) and np.isnan(d18o_cel)):
            o18_value = float(d18o_cel)
            print(f"✅ Usando valor único: {o18_value:.2f}‰")
        else:
            print(f"\n❌ ERRO: d18O_cel contém valor inválido!")
            print(f"📊 Valor encontrado: {d18o_cel} (tipo: {type(d18o_cel)})")
            print("\n💡 Solução:")
            print("   1. Corrija o valor de 'd18O_cel' no Firestore")
            print("   2. Ou forneça valor manualmente: python create_mapa_local.py DOC_ID VALOR_O18")
            return
    
    unknown_df = pd.DataFrame({
        'ID': [doc_data['id']],
        'O18': [o18_value]
    })
    
    print(f"\n📋 DataFrame preparado:")
    print(unknown_df)
    
    # 4. Configurar isoscape (OBRIGATÓRIO - oxygen_18_detailed.tiff)
    r_path = 'isoscapes/oxygen_18_detailed.tiff'
    
    if not os.path.exists(r_path):
        print(f"\n❌ ERRO: Isoscape não encontrado!")
        print(f"📁 Arquivo esperado: {r_path}")
        print("� Especificações:")
        print("   • Formato: GeoTIFF com 2 bandas (média + desvio padrão)")
        print("   • Resolução: 1024×1024 pixels (~4.3 km/pixel)")
        print("   • Isótopo: Oxigênio-18 (δ18O)")
        print("\n💡 Solução:")
        print("   1. Obtenha isoscape validado de δ18O para o Brasil")
        print(f"   2. Coloque em: {r_path}")
        print("   3. Ou use dados de teste: python create_example_isoscapes.py")
        return
    
    print(f"\n🗺️  Usando isoscape: {r_path}")
    
    # 4.5. Configurar máscara: Brasil inteiro OU recorte local ∩ Brasil
    mask_path = 'shapefiles/bra_admbnda_adm0_ibge_2020.shp'
    base_profile = None
    with rasterio.open(r_path) as src:
        base_profile = src.profile

    # Ler contorno do Brasil
    if not os.path.exists(mask_path):
        print(f"\n❌ ERRO: Shapefile do Brasil não encontrado!")
        print(f"📁 Arquivo esperado: {mask_path}")
        print("📊 Especificações:")
        print("   • Formato: ESRI Shapefile (.shp + .shx + .dbf + .prj)")
        print("   • Conteúdo: Contorno nacional do Brasil (IBGE 2020)")
        print("   • CRS: EPSG:4326 (WGS84)")
        print("\n💡 Solução:")
        print("   1. Baixe shapefiles do Brasil do IBGE")
        print("   2. Coloque em: shapefiles/bra_admbnda_adm0_ibge_2020.*")
        print("   3. Arquivos necessários:")
        print("      • bra_admbnda_adm0_ibge_2020.shp")
        print("      • bra_admbnda_adm0_ibge_2020.shx")
        print("      • bra_admbnda_adm0_ibge_2020.dbf")
        print("      • bra_admbnda_adm0_ibge_2020.prj")
        return

    prj_path = mask_path.replace('.shp', '.prj')
    if not os.path.exists(prj_path):
        print(f"\n❌ ERRO: Arquivo de projeção (.prj) não encontrado!")
        print(f"📁 Arquivo esperado: {prj_path}")
        print("\n💡 Solução:")
        print("   1. Baixe o conjunto completo de shapefiles do IBGE")
        print("   2. Ou crie manualmente com CRS EPSG:4326 (WGS84)")
        return

    brasil_gdf = gpd.read_file(mask_path)

    # Criar máscara local opcional
    local_mask_gdf = None
    if override_area_km2 is not None:
        lat = doc_data.get('lat') or doc_data.get('latitude')
        lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude')
        if lat is not None and lon is not None:
            print(f"\n📍 Criando recorte local em torno de ({lat}, {lon}) com área ≈ {override_area_km2} km²")
            local_mask_gdf = build_local_mask_from_point(lat, lon, override_area_km2, base_profile)
        else:
            print("\n⚠️  Lat/Lon ausentes na amostra; não é possível criar recorte local pela área. Usando máscara do Brasil inteiro.")

    # Interseção: se existir máscara local, usar (Brasil ∩ buffer); senão Brasil inteiro
    if local_mask_gdf is not None:
        print("\n�️  Usando máscara LOCAL (Brasil ∩ área em torno da amostra)")
        # Garantir CRS compatíveis
        if brasil_gdf.crs != local_mask_gdf.crs:
            brasil_gdf = brasil_gdf.to_crs(local_mask_gdf.crs)
        intersect_gdf = gpd.overlay(brasil_gdf, local_mask_gdf, how='intersection')
        if intersect_gdf.empty:
            print("\n⚠️  Interseção Brasil ∩ buffer vazia; revertendo para máscara Brasil inteiro.")
            effective_mask = brasil_gdf
        else:
            effective_mask = intersect_gdf
    else:
        print("\n�️  Usando máscara: Brasil inteiro (sem recorte local)")
        effective_mask = brasil_gdf
    
    print(f"\n📊 Modo: SINGLE-ISOSCAPE (apenas O18)")
    print(f"   • {r_path}")
    
    # 5. Criar diretório de output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(f"output_maps/{doc_id}_{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Pasta de output: {out_dir}")
    print("\n🚀 Executando pd_raster()...")
    print("=" * 70)
    
    try:
        # EXECUTAR A FUNÇÃO PRINCIPAL!
        result = pd_raster(
            r=r_path,  # String única para single-isoscape
            unknown=unknown_df,
            prior=None,
            mask=effective_mask,  # Brasil inteiro ou recorte local
            genplot=True,
            out_dir=out_dir
        )
        
        print("\n" + "=" * 70)
        print("✅ SUCESSO!")
        print("=" * 70)
        print(f"\n📊 Resultados gerados:")
        print(f"   • {len(result)} mapa(s) de probabilidade")
        print(f"   • Rasters GeoTIFF: {out_dir}")
        print(f"   • PDF: {out_dir}/output_pdRaster.pdf")
        
        # Abrir o PDF automaticamente
        pdf_path = f"{out_dir}/output_pdRaster.pdf"
        if os.path.exists(pdf_path):
            print(f"\n🌐 Abrindo PDF...")
            # Detectar sistema operacional e usar comando apropriado
            import platform
            if platform.system() == "Darwin":  # macOS
                os.system(f'open "{pdf_path}"')
            elif platform.system() == "Windows":
                os.system(f'start "" "{pdf_path}"')
            else:  # Linux
                os.system(f'xdg-open "{pdf_path}"')
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    main()
