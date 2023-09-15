import geopy.distance
import requests
import json
import ee

def fraud_detection_fetch_mapbiomas_alerts(value: dict):
    """
    Fetches MapBiomas alerts within a 10km radius of a given latitude and longitude,
    and adds the alerts to a dictionary of values for fraud detection.

    Args:
        value (dict): A dictionary containing the following keys:
            - lat (float): The latitude of the center point.
            - lon (float): The longitude of the center point.

    Returns:
        dict: A dictionary containing the same keys as the input dictionary, plus an 'alerts' key
        that maps to a list of alert dictionaries. Each alert dictionary contains the following keys:
            - alertCode (str): The code of the alert.
            - areaHa (float): The area of the alert in hectares.
            - detectedAt (str): The date and time when the alert was detected, in ISO 8601 format.
            - alertInsertedAt (str): The date and time when the alert was inserted into the MapBiomas database, in ISO 8601 format.
            - coordinates (dict): A dictionary containing the latitude and longitude of the alert.
            - url (str): The URL of the alert in the MapBiomas Alerta API.
            - distance_to_point (float): The distance between the alert and the center point, in kilometers.
            - images (dict): A dictionary containing the before and after images of the alert.
    """
    alerts = _fraud_detection_fetch_mapbiomas_alerts(float(value.get('lat')), float(value.get('lon'))) 
    value["alerts"] = alerts
    return value

def _fraud_detection_fetch_mapbiomas_alerts(lat: float, lon: float):
    point = ee.Geometry.Point(lon, lat)
    radius_10km_buffer = point.buffer(10000)
    
    list_coords = ee.Array.cat(radius_10km_buffer.bounds().coordinates(), 1);

    # get the X-coordinates
    xCoords = list_coords.slice(1, 0, 1)
    yCoords = list_coords.slice(1, 1, 2)

    # reduce the arrays to find the max (or min) value
    # e.g. defining a square with 2 points: the top left and bottom right
    xMin = xCoords.reduce('min', [0]).get([0,0]).getInfo()
    xMax = xCoords.reduce('max', [0]).get([0,0]).getInfo()
    yMin = yCoords.reduce('min', [0]).get([0,0]).getInfo()
    yMax = yCoords.reduce('max', [0]).get([0,0]).getInfo()

    # create GraphQL API request
    url = "https://plataforma.alerta.mapbiomas.org/api/v1/graphql"
    query = """
    query published_alerts {
        publishedAlerts(limit: 20, offset: 0, boundingBox: [%s, %s, %s, %s]) {
            alertCode
            areaHa
            detectedAt
            alertInsertedAt
            coordinates {
                latitude
                longitude
            }
        }
    }
    """ % (xMin, yMin, xMax, yMax)

    # Make the request
    main_alerts_response = requests.post(url, headers={
        "Content-Type": "application/json"
    }, data=json.dumps({"query":query}))

    alert_code_to_metadata = {alert["alertCode"]:alert for alert in main_alerts_response.json()['data']['publishedAlerts']}

    for alert_code in alert_code_to_metadata.keys():
        query = """
        query alert_report {
            alertReport(alertCode: %s){
                alertCode
                carCode
                source
                images {
                    after {
                        satellite
                        url
                    }
                    before {
                        satellite
                        url
                    }
                }
            }
        }
        """ % alert_code

        # Make the request
        response = requests.post(url, headers={
            "Content-Type": "application/json"
        }, data=json.dumps({"query":query}))
        
        if "data" in response.json():
            alert_response_with_images = response.json()['data']['alertReport']
            alert_code_to_metadata[alert_code] |= alert_response_with_images["images"]
            alert_code_to_metadata[alert_code]["url"] = "https://plataforma.alerta.mapbiomas.org/laudo/%s" % alert_response_with_images['alertCode']

            coordinates = alert_code_to_metadata[alert_code]["coordinates"]
            coordinates_tuple = (coordinates["latitude"], coordinates["longitude"])

            alert_code_to_metadata[alert_code]["distance_to_point"] = geopy.distance.distance((lat, lon), coordinates_tuple).km
    
    return list(alert_code_to_metadata.values())


