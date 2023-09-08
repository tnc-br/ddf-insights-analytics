import ee
import geemap
from google.cloud import storage
import os

def fraud_detection_generate_map_and_upload_to_gcs(lat: float, lon: float, document_id):
    """
    Generates a land use map centered on a given latitude and longitude, and uploads it to Google Cloud Storage.

    Args:
        lat (float): The latitude of the center point of the map.
        lon (float): The longitude of the center point of the map.
        document_id (str): The ID of the document to be uploaded to GCS.

    Returns:
        None.
    """

    point = ee.Geometry.Point(lon, lat)
    radius_1km_buffer = point.buffer(1000)
    radius_10km_buffer = point.buffer(10000)

    # load MapBiomas Brazil deforestation + land use dataset
    land_use_repo_mapbiomas = ee.Image(
        "projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1"
    )
    land_use_layers_2021_simplified = (
        land_use_repo_mapbiomas.select("product_2021").divide(100).floor()
    )
    full_brazil_geometry_with_10km_radius_hole = (
        land_use_repo_mapbiomas.mask().geometry().difference(radius_10km_buffer)
    )

    # display the full land use map
    vis_params = {
        "min": 1,
        "max": 7,
        "palette": [
            "#fffbc2",  # 1, 'Anthropic'
            "#09611f",  # 2, 'Primary Vegetation'
            "#4ea376",  # 3, 'Secondary Vegetation'
            "#e31a1c",  # 4, 'Deforestation in  Primary Vegetation'
            "#94fc03",  # 5, 'Secondary Vegetation Regrowth'
            "#ffa500",  # 6, 'Deforestation in Secondary Vegetation'
            "#212121",  # 7, 'Not applied'
        ],
    }

    # show it in a map
    Map = geemap.Map()

    Map.addLayer(land_use_layers_2021_simplified, vis_params, "Brazil")
    Map.addLayer(full_brazil_geometry_with_10km_radius_hole, {}, "10 km radius mask")
    Map.addLayer(radius_1km_buffer, {"color": "white"}, "1 km radius mask")
    Map.centerObject(radius_10km_buffer, 11)

    # upload map to GCS
    download_dir = os.getcwd()
    html_file = os.path.join(download_dir, f"{document_id}.html")
    Map.to_html(
        filename=html_file, title="Land Use details", width="100%", height="300px"
    )
    storage_client = storage.Client()
    bucket = storage_client.bucket("timberid-maps")
    blob = bucket.blob(document_id)
    blob.upload_from_filename(html_file)

    print(f"Uploaded file blob with id: {blob.id}")
