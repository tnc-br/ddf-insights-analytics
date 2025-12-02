from typing import Literal, Optional, Union
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from pathlib import Path


def qtl_raster(
    pd_raster: Union[str, Path, rasterio.DatasetReader],
    threshold: float,
    threshold_type: Literal["area", "prob"] = "area",
    gen_plot: bool = True,
    out_dir: Optional[Union[str, Path]] = None,
) -> np.ndarray:
    """
    Gera um mapa binário de quantis a partir de um raster de densidade de probabilidade.

    Parameters
    ----------
    pd_raster : str, Path ou rasterio.DatasetReader
        Caminho para o arquivo raster ou objeto rasterio aberto.
    threshold : float
        Valor entre 0 e 1 para definir o limiar.
    threshold_type : {"area", "prob"}, default="area"
        Tipo de limiar:
        - "area": top X% da área (quantil)
        - "prob": top X% da probabilidade acumulada
    gen_plot : bool, default=True
        Se True, gera plots dos resultados.
    out_dir : str, Path ou None, default=None
        Diretório para salvar os plots em PDF. Se None, não salva.

    Returns
    -------
    np.ndarray
        Array booleano (ou stack de arrays) com as regiões acima do limiar.

    Raises
    ------
    ValueError
        Se threshold não estiver entre 0 e 1, ou threshold_type for inválido.
    TypeError
        Se pd_raster não for um tipo válido.
    """
    # Validações
    if not isinstance(threshold, (int, float)):
        raise TypeError("threshold must be a number between 0 and 1")
    
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    
    if threshold_type not in ["area", "prob"]:
        raise ValueError("threshold_type must be 'area' or 'prob'")
    
    if not isinstance(gen_plot, bool):
        print("gen_plot should be boolean (True or False), using default = True")
        gen_plot = True
    
    # Processar out_dir
    if out_dir is not None:
        out_dir = Path(out_dir)
        if not out_dir.exists():
            print(f"out_dir does not exist, creating: {out_dir}")
            out_dir.mkdir(parents=True, exist_ok=True)
    
    # Abrir raster
    if isinstance(pd_raster, (str, Path)):
        with rasterio.open(pd_raster) as src:
            data = src.read()  # shape: (n_bands, height, width)
            profile = src.profile
            band_names = src.descriptions or [f"Band {i+1}" for i in range(src.count)]
    elif isinstance(pd_raster, rasterio.DatasetReader):
        data = pd_raster.read()
        profile = pd_raster.profile
        band_names = pd_raster.descriptions or [f"Band {i+1}" for i in range(pd_raster.count)]
    else:
        raise TypeError("pd_raster must be a file path or rasterio.DatasetReader")
    
    n_bands = data.shape[0]
    result = np.zeros_like(data, dtype=bool)
    cuts = np.zeros(n_bands)
    
    # Calcular limiares
    for i in range(n_bands):
        band_data = data[i]
        valid_data = band_data[~np.isnan(band_data)].flatten()
        
        if len(valid_data) == 0:
            print(f"Warning: Band {i+1} has no valid data")
            continue
        
        if threshold == 0:
            cuts[i] = np.max(valid_data) + 1  # nada passa
        elif threshold == 1:
            cuts[i] = np.min(valid_data) - 1  # tudo passa
        else:
            if threshold_type == "prob":
                # Probabilidade acumulada
                sorted_data = np.sort(valid_data)
                cumsum = np.cumsum(sorted_data)
                total = cumsum[-1]
                
                # Busca binária para encontrar o corte
                idx = np.searchsorted(cumsum, total * (1 - threshold))
                cuts[i] = sorted_data[idx] if idx < len(sorted_data) else sorted_data[-1]
                
            elif threshold_type == "area":
                # Quantil (top X% da área)
                cuts[i] = np.quantile(valid_data, 1 - threshold)
        
        result[i] = band_data > cuts[i]
    
    # Gerar títulos
    title_type = "probability" if threshold_type == "prob" else "area"
    if n_bands > 1:
        titles = [
            f"Top {threshold*100:.1f}% by {title_type} for {band_names[i]}"
            for i in range(n_bands)
        ]
    else:
        titles = [f"Top {threshold*100:.1f}% by {title_type}"]
    
    # Plotar
    if gen_plot:
        fig, axes = plt.subplots(1, n_bands, figsize=(6 * n_bands, 5))
        if n_bands == 1:
            axes = [axes]
        
        for i, (ax, title) in enumerate(zip(axes, titles)):
            ax.imshow(result[i], cmap="gray", interpolation="nearest")
            ax.set_title(title)
            ax.axis("off")
        
        plt.tight_layout()
        plt.show()
    
    # Salvar PDF
    if out_dir is not None:
        pdf_path = out_dir / "qtl_raster_result.pdf"
        
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages(pdf_path) as pdf:
            for i, title in enumerate(titles):
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(result[i], cmap="gray", interpolation="nearest")
                ax.set_title(title)
                ax.axis("off")
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
        
        print(f"PDF saved to: {pdf_path}")
    
    return result