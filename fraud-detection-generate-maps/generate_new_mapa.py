import os
import warnings
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import reproject, Resampling
from scipy.stats import norm, multivariate_normal
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Helper function to compare raster geometries (crs, transform, shape)
def compare_geom(r1_profile, r2_profile):
    """
    Compares the geometry of two rasterio profiles.
    Raises an error if they don't match.
    
    Args:
        r1_profile: Rasterio profile dictionary from first raster
        r2_profile: Rasterio profile dictionary from second raster
        
    Returns:
        bool: True if geometries match
        
    Raises:
        ValueError: If CRS, transform, or dimensions don't match
    """
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

# -----------------------------------------------------------------------------
# Processing and Validation Functions (Translated from R's 'check' functions)
# -----------------------------------------------------------------------------

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

    # Check for missing values
    if unknown.isnull().values.any():
        raise ValueError("Missing values (NaN) detected in unknown.")

    # Check data types
    for col in unknown.columns[1:]:
        if not pd.api.types.is_numeric_dtype(unknown[col]):
            raise TypeError(f"Unknown data column '{col}' must contain numeric values.")

    return unknown

def check_prior(prior_path, r_profile):
    """Validates the prior raster."""
    if prior_path is None:
        return None, None

    with rasterio.open(prior_path) as prior_src:
        prior_profile = prior_src.profile
        if not prior_profile['crs']:
            raise ValueError("Prior must have a valid coordinate reference system.")

        # Reproject if necessary (note: this is a simplified in-memory reprojection)
        if prior_profile['crs'] != r_profile['crs']:
            warnings.warn("Prior was reprojected to match isoscape CRS.")
            # This is a complex operation; for simplicity, we raise an error
            # A full implementation would use rasterio.warp.reproject
            raise NotImplementedError("Automatic reprojection of 'prior' is not implemented. Please ensure CRS match.")

        # Check geometry
        compare_geom(prior_profile, r_profile)

        prior_values = prior_src.read(1).flatten()
        return prior_values, prior_profile

def check_mask(mask_path, r_profile):
    """Validates the mask vector file."""
    if mask_path is None:
        return None

    mask_gdf = gpd.read_file(mask_path)
    if not mask_gdf.crs:
        raise ValueError("Mask must have a valid coordinate reference system.")

    if not all(mask_gdf.geom_type.isin(['Polygon', 'MultiPolygon'])):
        raise ValueError("Mask geometry must be polygons.")

    # Reproject if CRS differs
    if mask_gdf.crs != r_profile['crs']:
        warnings.warn("Mask was reprojected to match isoscape CRS.")
        mask_gdf = mask_gdf.to_crs(r_profile['crs'])

    return mask_gdf

def check_options(genplot, out_dir):
    """Validates plotting and output directory options."""
    if not isinstance(genplot, bool):
        raise TypeError("genplot should be boolean (True or False).")

    if out_dir is not None:
        if not isinstance(out_dir, str):
            raise TypeError("out_dir should be a character string.")
        if not os.path.exists(out_dir):
            print(f"out_dir '{out_dir}' does not exist, creating.")
            os.makedirs(out_dir)

def write_out(out_dir, genplot, result_stack, data, base_profile):
    """Handles plotting and file writing."""
    n_samples = len(result_stack)
    if n_samples == 0:
        return
    
    # Limit plotting to avoid memory issues with large datasets
    MAX_PLOTS = 50
    if n_samples > MAX_PLOTS:
        warnings.warn(f"Number of samples ({n_samples}) exceeds maximum plots ({MAX_PLOTS}). "
                     f"Only plotting first {MAX_PLOTS} samples.")
        plot_count = MAX_PLOTS
    else:
        plot_count = n_samples

    pdf_path = None
    if out_dir is not None:
        pdf_path = os.path.join(out_dir, "output_pdRaster.pdf")

    if genplot:
        if plot_count > 1:
            # Create a grid for plotting
            cols = 5
            rows = int(np.ceil(plot_count / cols))
            fig, axes = plt.subplots(rows, cols, figsize=(15, 3 * rows), squeeze=False)
            axes = axes.flatten()
        else:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            axes = [ax]

        for i in range(plot_count):
            img = result_stack[i].reshape(base_profile['height'], base_profile['width'])
            
            # Mascarar valores nodata para visualização correta
            nodata = base_profile.get('nodata', -9999)
            img_masked = np.ma.masked_where(img == nodata, img)
            
            # Normalizar valores válidos para escala 0-1
            valid_data = img_masked.compressed()
            if len(valid_data) > 0:
                vmin = valid_data.min()
                vmax = valid_data.max()
            else:
                vmin, vmax = 0, 1
            
            im = axes[i].imshow(img_masked, cmap='viridis', vmin=vmin, vmax=vmax, interpolation='nearest')
            axes[i].set_title(data.iloc[i, 0])
            axes[i].set_xticks([])
            axes[i].set_yticks([])
            fig.colorbar(im, ax=axes[i], label='Probability Density')

        # Hide unused subplots
        for j in range(plot_count, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()

        if pdf_path:
            plt.savefig(pdf_path, format='pdf')
        else:
            plt.show()

# -----------------------------------------------------------------------------
# Core Probability Density Functions
# -----------------------------------------------------------------------------

def _pd_raster_default(r_path, unknown, prior=None, mask=None, genplot=True, out_dir=None):
    """Handles single isoscape (2-band raster) assignment."""
    with rasterio.open(r_path) as src:
        # Validate CRS exists (critical for geospatial operations)
        if not src.crs:
            raise ValueError("Raster must have a valid coordinate reference system (CRS).")
        if src.count != 2:
            raise ValueError("r should be a raster with two layers (mean and standard deviation).")

        profile = src.profile
        transform = src.transform

        # Apply mask if provided
        if mask is not None:
            mean_data, transform = rio_mask(src, shapes=mask.geometry, crop=True, indexes=1)
            sd_data, _ = rio_mask(src, shapes=mask.geometry, crop=True, indexes=2)
            # indexes=1 (not [1]) returns 2D array directly (height, width)
            mean_data = mean_data.astype(profile['dtype'])
            sd_data = sd_data.astype(profile['dtype'])
            profile.update({
                'height': mean_data.shape[0],
                'width': mean_data.shape[1],
                'transform': transform
            })
        else:
            mean_data = src.read(1)
            sd_data = src.read(2)

    mean_v = mean_data.flatten()
    error_v = sd_data.flatten()

    # Exclude NoData cells from calculation
    valid_mask = (mean_v != profile['nodata']) & (error_v != profile['nodata'])
    mean_v = mean_v[valid_mask]
    error_v = error_v[valid_mask]

    prior_v, _ = check_prior(prior, profile)
    if prior_v is not None:
        prior_v = prior_v[valid_mask]

    result_stack = []

    for i in range(len(unknown)):
        indv_data = unknown.iloc[i]
        indv_id = indv_data.iloc[0]
        indv_iso_val = indv_data.iloc[1]

        # Calculate normal probability density
        assign = norm.pdf(indv_iso_val, loc=mean_v, scale=error_v)

        if prior_v is not None:
            assign = assign * prior_v

        assign_sum = np.sum(assign)
        if assign_sum > 0:
            assign_norm = assign / assign_sum
        else:
            # If all probabilities are zero, create uniform distribution over valid cells
            warnings.warn(f"Sample {indv_id}: All probabilities are zero. Using uniform distribution.")
            assign_norm = np.ones_like(assign) / len(assign) if len(assign) > 0 else assign

        # Create a full raster array with NoData values
        full_assign_norm = np.full(profile['height'] * profile['width'], profile['nodata'], dtype=np.float32)
        full_assign_norm[valid_mask] = assign_norm
        result_stack.append(full_assign_norm)

        if out_dir:
            filename = os.path.join(out_dir, f"{indv_id}_like.tif")
            profile.update(dtype=rasterio.float32, count=1, nodata=-9999)
            with rasterio.open(filename, 'w', **profile) as dst:
                dst.write(full_assign_norm.reshape(profile['height'], profile['width']), 1)

    write_out(out_dir, genplot, result_stack, unknown, profile)

    return result_stack

def _pd_raster_iso_stack(r_paths, unknown, prior=None, mask=None, genplot=True, out_dir=None):
    """Handles multiple isoscapes (list of 2-band rasters) assignment."""
    ni = len(r_paths)

    # Open first raster to get base profile and apply mask
    with rasterio.open(r_paths[0]) as src:
        if not src.crs:
            raise ValueError("First raster must have a valid coordinate reference system (CRS).")
        base_profile = src.profile
        transform = src.transform
        if mask is not None:
            mean_data, transform = rio_mask(src, shapes=mask.geometry, crop=True, indexes=1)
            sd_data, _ = rio_mask(src, shapes=mask.geometry, crop=True, indexes=2)
            # indexes=1 (not [1]) returns 2D array directly (height, width)
            base_profile.update({
                'height': mean_data.shape[0],
                'width': mean_data.shape[1],
                'transform': transform
            })
        else:
            mean_data = src.read(1)
            sd_data = src.read(2)

    # Initialize arrays to hold all isoscape data
    mean_v = [mean_data.flatten()]
    error_v = [sd_data.flatten()]

    # Read and process remaining isoscapes
    for i in range(1, ni):
        with rasterio.open(r_paths[i]) as src:
            # Only compare geometry if no mask (mask changes transform)
            if mask is None:
                compare_geom(src.profile, base_profile)
            if mask is not None:
                mean_data_i, _ = rio_mask(src, shapes=mask.geometry, crop=True, indexes=1)
                sd_data_i, _ = rio_mask(src, shapes=mask.geometry, crop=True, indexes=2)
                # indexes=1 (not [1]) returns 2D array directly (height, width)
            else:
                mean_data_i = src.read(1)
                sd_data_i = src.read(2)
            mean_v.append(mean_data_i.flatten())
            error_v.append(sd_data_i.flatten())

    mean_v = np.vstack(mean_v).T
    error_v = np.vstack(error_v).T

    # Identify valid cells (where no layer has a NoData value)
    valid_mask = ~np.any((mean_v == base_profile['nodata']) | (error_v == base_profile['nodata']), axis=1)
    mean_v_valid = mean_v[valid_mask, :]
    error_v_valid = error_v[valid_mask, :]

    # Sanity check for highly correlated isoscapes
    corr_matrix = pd.DataFrame(mean_v_valid).corr()**2
    np.fill_diagonal(corr_matrix.values, np.nan)
    if np.nanmax(corr_matrix.values) > 0.7:
        warnings.warn("Two or more isoscapes have shared variance > 0.7; added information "
                      "will be limited, and specificity of assignments may be inflated.")

    # Pre-calculate covariance matrices for each cell (the most intensive part)
    # This logic replicates the per-cell covariance calculation from the R script
    # NOTE: This approach can consume significant memory for large rasters
    # Consider processing in batches if memory issues occur
    dev = pd.DataFrame(mean_v_valid).cov().values
    v = np.sqrt(np.diag(dev))
    
    # Memory warning for large datasets
    n_valid_cells = mean_v_valid.shape[0]
    estimated_mb = (n_valid_cells * ni * ni * 8) / (1024 * 1024)  # 8 bytes per float64
    if estimated_mb > 1000:  # More than 1GB
        warnings.warn(f"Large dataset detected: {n_valid_cells} cells will require ~{estimated_mb:.0f}MB "
                     f"for covariance matrices. Consider using batch processing for very large rasters.")
    
    d_l = []
    for i in range(mean_v_valid.shape[0]):
        v_cell = error_v_valid[i, :] / v
        # Use broadcasting for efficient element-wise multiplication
        d_cell = dev * np.outer(v_cell, v_cell)
        d_l.append(d_cell)

    prior_v, _ = check_prior(prior, base_profile)
    if prior_v is not None:
        prior_v = prior_v[valid_mask]

    result_stack = []

    for i in range(len(unknown)):
        indv_data = unknown.iloc[i]
        indv_id = indv_data.iloc[0]
        indv_iso = indv_data.iloc[1:].values.astype(float)

        # Calculate multivariate normal PDF for each valid cell
        assign_valid = np.zeros(mean_v_valid.shape[0])
        for j in range(mean_v_valid.shape[0]):
            try:
                assign_valid[j] = multivariate_normal.pdf(indv_iso, mean=mean_v_valid[j, :], cov=d_l[j])
            except np.linalg.LinAlgError:
                assign_valid[j] = 0 # If covariance is singular, probability is 0

        if prior_v is not None:
            assign_valid *= prior_v

        assign_sum = np.sum(assign_valid)
        if assign_sum > 0:
            assign_norm_valid = assign_valid / assign_sum
        else:
            # If all probabilities are zero, create uniform distribution
            warnings.warn(f"Sample {indv_id}: All probabilities are zero. Using uniform distribution.")
            assign_norm_valid = np.ones_like(assign_valid) / len(assign_valid) if len(assign_valid) > 0 else assign_valid

        # Create a full raster array with NoData values
        full_assign_norm = np.full(base_profile['height'] * base_profile['width'], base_profile['nodata'], dtype=np.float32)
        full_assign_norm[valid_mask] = assign_norm_valid
        result_stack.append(full_assign_norm)

        if out_dir:
            filename = os.path.join(out_dir, f"{indv_id}_like.tif")
            base_profile.update(dtype=rasterio.float32, count=1, nodata=-9999)
            with rasterio.open(filename, 'w', **base_profile) as dst:
                dst.write(full_assign_norm.reshape(base_profile['height'], base_profile['width']), 1)

    write_out(out_dir, genplot, result_stack, unknown, base_profile)

    return result_stack

# -----------------------------------------------------------------------------
# Main Public Function (Dispatcher)
# -----------------------------------------------------------------------------

def pd_raster(r, unknown, prior=None, mask=None, genplot=True, out_dir=None):
    """
    Calculates the probability density of origin for unknown samples based on one or more isoscapes.
    
    This function serves as a dispatcher, similar to R's S3 methods.
    
    Args:
        r (str or list): Path to a 2-band (mean, sd) GeoTIFF for a single isoscape,
                         or a list of paths for multiple isoscapes ('isoStack').
        unknown (pd.DataFrame or dict or list): A DataFrame with sample data (ID, value1, ...).
                                                Can also be a dict (or list of dicts)
                                                representing 'refTrans' objects.
        prior (str, optional): Path to a single-band GeoTIFF with prior probabilities. Defaults to None.
        mask (str, optional): Path to a polygon vector file (e.g., Shapefile, GeoPackage)
                              to mask the analysis area. Defaults to None.
        genplot (bool, optional): Whether to generate and display/save plots. Defaults to True.
        out_dir (str, optional): Directory to save output rasters and plots. Defaults to None.
    Returns:
        list: A list of numpy arrays, where each array is a flattened probability surface
              for one of the unknown samples.
    """
    # Validate options first
    check_options(genplot, out_dir)

    # Dispatch based on the type of 'r'
    if isinstance(r, list):
        # This corresponds to the pdRaster.isoStack method in R
        print("Running in multi-isoscape (isoStack) mode.")
        n_isoscapes = len(r)
        data = check_unknown(unknown, n_isoscapes)
        
        # Cache profile to avoid redundant file read
        with rasterio.open(r[0]) as src:
            base_profile = src.profile
        mask_gdf = check_mask(mask, base_profile)
        return _pd_raster_iso_stack(r, data, prior, mask_gdf, genplot, out_dir)

    elif isinstance(r, str):
        # This corresponds to the pdRaster.default method in R
        print("Running in single-isoscape (default) mode.")
        n_isoscapes = 1
        data = check_unknown(unknown, n_isoscapes)
        
        # Cache profile to avoid redundant file read
        with rasterio.open(r) as src:
            base_profile = src.profile
        mask_gdf = check_mask(mask, base_profile)
        return _pd_raster_default(r, data, prior, mask_gdf, genplot, out_dir)

    else:
        raise TypeError("Argument 'r' must be a string (filepath) or a list of strings.")




