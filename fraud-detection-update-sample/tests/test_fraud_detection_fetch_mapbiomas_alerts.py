import unittest
import requests
import json

class TestFraudDetectionFetchMapbiomasAlerts(unittest.TestCase):

    # You can find the API endpoint documentation here: https://plataforma.alerta.mapbiomas.org/sign-in?callback_url=/api
    # (Uou need to be logged in to see it, register if needed)

    def test_mapbiomas_alerta_endpoints_contracts(self):
        url = "https://plataforma.alerta.mapbiomas.org/api/v1/graphql"

        xMin = -61.396529589347374
        yMin = -2.28567265927422
        xMax = -56.4672263233907
        yMax = -5.3358645009758465

        # TEST PUBLISHED ALERTS
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

        response = requests.post(url, headers={
            "Content-Type": "application/json",
        }, data=json.dumps({"query":query}))

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the expected keys
        published_alerts_data = response.json()["data"]["publishedAlerts"]

        first_elem = published_alerts_data[1]
        self.assertIn("alertCode", first_elem)
        self.assertIn("areaHa", first_elem)
        self.assertIn("detectedAt", first_elem)
        self.assertIn("alertInsertedAt", first_elem)
        self.assertIn("coordinates", first_elem)
        self.assertIn("latitude", first_elem["coordinates"])
        self.assertIn("longitude", first_elem["coordinates"])

        # TEST ALERT REPORT
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
        """ % first_elem["alertCode"]

        # Make the request
        response = requests.post(url, headers={
            "Content-Type": "application/json"
        }, data=json.dumps({"query":query}))
        
        alert_report_data = response.json()["data"]["alertReport"]

        self.assertIn("alertCode", alert_report_data)
        self.assertIn("images", alert_report_data)
        self.assertIn("before", alert_report_data["images"])
        self.assertIn("after", alert_report_data["images"])
        self.assertIn("url", alert_report_data["images"]["before"])
        self.assertIn("url", alert_report_data["images"]["after"])
