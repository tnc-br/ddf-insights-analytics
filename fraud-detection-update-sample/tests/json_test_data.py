full_json_data_example = """
{
  "sample_name": "test sample validity",
  "created_on": "8-9-2023",
  "d18O_cel": [
    "123"
  ],
  "species": "Hymenaea courbaril",
  "trusted": "untrusted",
  "status": "concluded",
  "last_updated_by": "Josh Wolkoff",
  "validity_details": {
    "p_value_oxygen": 0.001193676470473496,
    "p_value_nitrogen": 0.010445452763826784,
    "p_value_carbon": 0.00034070435105630674
  },
  "validity": 4.248069198730162e-9,
  "code_lab": "fd1239d5488215a23440",
  "n_wood": [
    12
  ],
  "lat": -13.0845,
  "land_use_anthropic_pct": {
    "2011": 0.45034623326325146,
    "2012": 0.44770272211177214,
    "2013": 0.4482117137641799,
    "2014": 0.45126455395621806,
    "2015": 0.45269307757612276,
    "2016": 0.4553281223992332,
    "2017": 0.4587216170736057,
    "2018": 0.4577154170252487,
    "2019": 0.4601431958992026,
    "2020": 0.46499305682441266,
    "2021": 0.46557667144547044
  },
  "created_by_name": "Josh Wolkoff",
  "site": "Test site",
  "land_use_secondary_vegetation_or_regrowth_pct": {
    "2011": 0.03598910624493149,
    "2012": 0.03915637563997758,
    "2013": 0.04057287060076802,
    "2014": 0.04046374206638375,
    "2015": 0.04049680433999142,
    "2016": 0.040145821726395824,
    "2017": 0.0410765192049453,
    "2018": 0.04309859563181422,
    "2019": 0.045395060747033804,
    "2020": 0.041656724146054556,
    "2021": 0.04162850673609025
  },
  "collected_by": "supplier",
  "carbon": [
    16,
    14,
    18
  ],
  "c_wood": [
    12
  ],
  "visibility": "public",
  "municipality": "Vilhena",
  "oxygen": [
    22,
    23,
    24
  ],
  "land_use_primary_vegetation_pct": {
    "2011": 0.513664660491817,
    "2012": 0.5131409022482503,
    "2013": 0.5112154156350521,
    "2014": 0.5082717039773982,
    "2015": 0.5068101180838858,
    "2016": 0.504526055874371,
    "2017": 0.5002018637214489,
    "2018": 0.49918598734293695,
    "2019": 0.49446174335376347,
    "2020": 0.49335021902953274,
    "2021": 0.49279482181843925
  },
  "org_name": "t1QbuSDmOrvG1Khp9Vf2",
  "c_cel": [
    12
  ],
  "amount_of_measurementste": "3",
  "nitrogen": [
    -21,
    -29,
    -18
  ],
  "water_pct": {
    "is_point_water": false,
    "water_mean_in_10km_buffer": 0.0070068910493711264,
    "water_mean_in_1km_buffer": 0
  },
  "d13C_cel": [
    12
  ],
  "alerts": [
    {
      "areaHa": 235.6794,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/11368/after_deforestation.png",
        "satellite": "Sentinel-2"
      },
      "detectedAt": "15/05/2019",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/11368",
      "distance_to_point": 9.632019033764433,
      "alertCode": "11368",
      "coordinates": {
        "latitude": -13.025003713251833,
        "longitude": -53.314664066568064
      },
      "alertInsertedAt": "10/02/2020 21:00",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/11368/before_deforestation.png",
        "satellite": "Sentinel-2"
      }
    },
    {
      "areaHa": 18.9988,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/11367/after_deforestation.png",
        "satellite": "Sentinel-2"
      },
      "detectedAt": "01/06/2019",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/11367",
      "distance_to_point": 9.927289765505702,
      "alertCode": "11367",
      "coordinates": {
        "latitude": -13.00903494579343,
        "longitude": -53.32998011468373
      },
      "alertInsertedAt": "10/02/2020 21:00",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/11367/before_deforestation.png",
        "satellite": "Sentinel-2"
      }
    },
    {
      "areaHa": 2.4115,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/5571/after_deforestation.png",
        "satellite": "Sentinel-2"
      },
      "detectedAt": "12/07/2019",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/5571",
      "distance_to_point": 10.411265241165296,
      "alertCode": "5571",
      "coordinates": {
        "latitude": -13.005847378060828,
        "longitude": -53.32679514170368
      },
      "alertInsertedAt": "10/02/2020 21:00",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/5571/before_deforestation.png",
        "satellite": "Sentinel-2"
      }
    },
    {
      "areaHa": 11.1369,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/124511/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/02/2020",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/124511",
      "distance_to_point": 8.313740686634866,
      "alertCode": "124511",
      "coordinates": {
        "latitude": -13.02964505305971,
        "longitude": -53.327108268237325
      },
      "alertInsertedAt": "25/05/2020 20:16",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/124511/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 376.8583,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/146309/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/01/2020",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/146309",
      "distance_to_point": 10.470979731041876,
      "alertCode": "146309",
      "coordinates": {
        "latitude": -13.014877945313987,
        "longitude": -53.31410154356042
      },
      "alertInsertedAt": "16/07/2020 12:41",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/146309/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 0.8159,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/152015/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/05/2020",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/152015",
      "distance_to_point": 10.119937317264345,
      "alertCode": "152015",
      "coordinates": {
        "latitude": -13.00716610417982,
        "longitude": -53.32966625614848
      },
      "alertInsertedAt": "16/07/2020 12:41",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/152015/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 6.1253,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/245561/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/09/2020",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/245507",
      "distance_to_point": 3.378018118875003,
      "alertCode": "245507",
      "coordinates": {
        "latitude": -13.084562238961293,
        "longitude": -53.41064869358061
      },
      "alertInsertedAt": "23/11/2020 21:43",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/245561/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 2.6038,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/303882/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/12/2020",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/303804",
      "distance_to_point": 11.448255561171845,
      "alertCode": "303804",
      "coordinates": {
        "latitude": -13.000551445844064,
        "longitude": -53.31778564753191
      },
      "alertInsertedAt": "13/02/2021 14:17",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/303882/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 9.9544,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/338452/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/05/2021",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/337626",
      "distance_to_point": 12.249578490443024,
      "alertCode": "337626",
      "coordinates": {
        "latitude": -13.145135892903571,
        "longitude": -53.28497787987658
      },
      "alertInsertedAt": "16/06/2021 11:14",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/338452/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 3.645,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/355610/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/01/2020",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/354784",
      "distance_to_point": 11.786577786009133,
      "alertCode": "354784",
      "coordinates": {
        "latitude": -12.998218304624865,
        "longitude": -53.44324640087431
      },
      "alertInsertedAt": "20/07/2021 20:29",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/355610/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 5.8914,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/399164/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/07/2021",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/398323",
      "distance_to_point": 13.464351265159584,
      "alertCode": "398323",
      "coordinates": {
        "latitude": -13.178970081162452,
        "longitude": -53.457789064659195
      },
      "alertInsertedAt": "21/08/2021 20:50",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/399164/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 29.214,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/414604/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/07/2021",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/413262",
      "distance_to_point": 11.94394646773228,
      "alertCode": "413262",
      "coordinates": {
        "latitude": -13.167051807723746,
        "longitude": -53.450489200692225
      },
      "alertInsertedAt": "10/09/2021 07:50",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/414604/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 0.6101,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/500266/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/06/2021",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/498908",
      "distance_to_point": 11.962065417627725,
      "alertCode": "498908",
      "coordinates": {
        "latitude": -12.994699976828834,
        "longitude": -53.44092725550593
      },
      "alertInsertedAt": "31/01/2022 10:40",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/500266/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 0.4007,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/501877/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/09/2021",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/500519",
      "distance_to_point": 11.997867679021523,
      "alertCode": "500519",
      "coordinates": {
        "latitude": -12.997213608936516,
        "longitude": -53.44514544160795
      },
      "alertInsertedAt": "31/01/2022 13:04",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/501877/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 96.9682,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/563158/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "15/01/2022",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/561670",
      "distance_to_point": 12.41087302164786,
      "alertCode": "561670",
      "coordinates": {
        "latitude": -13.138757716647726,
        "longitude": -53.27932382960241
      },
      "alertInsertedAt": "24/05/2022 17:08",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/563158/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 80.5689,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/574931/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/02/2022",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/573443",
      "distance_to_point": 12.067093094153094,
      "alertCode": "573443",
      "coordinates": {
        "latitude": -13.15831356218177,
        "longitude": -53.2975662287035
      },
      "alertInsertedAt": "24/05/2022 23:39",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/574931/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 4.4139,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/600014/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/05/2022",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/598526",
      "distance_to_point": 11.01548890454279,
      "alertCode": "598526",
      "coordinates": {
        "latitude": -13.143667047067119,
        "longitude": -53.29779479726426
      },
      "alertInsertedAt": "06/07/2022 14:44",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/600014/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 76.4901,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/878295/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/01/2023",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/876807",
      "distance_to_point": 12.030244027746942,
      "alertCode": "876807",
      "coordinates": {
        "latitude": -13.023211309248317,
        "longitude": -53.471121926834336
      },
      "alertInsertedAt": "26/03/2023 20:51",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/878295/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 0.6827,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/874951/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/01/2023",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/873463",
      "distance_to_point": 11.922247339269765,
      "alertCode": "873463",
      "coordinates": {
        "latitude": -12.998344646700122,
        "longitude": -53.445527798937
      },
      "alertInsertedAt": "26/03/2023 19:05",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/874951/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    },
    {
      "areaHa": 5.6893,
      "after": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/875235/after_deforestation.png",
        "satellite": "PlanetScope"
      },
      "detectedAt": "01/12/2022",
      "url": "https://plataforma.alerta.mapbiomas.org/laudo/873747",
      "distance_to_point": 9.914889285489444,
      "alertCode": "873747",
      "coordinates": {
        "latitude": -13.012812142583446,
        "longitude": -53.3246401793921
      },
      "alertInsertedAt": "26/03/2023 19:05",
      "before": {
        "url": "https://storage.googleapis.com/alerta-public/IMAGES/875235/before_deforestation.png",
        "satellite": "PlanetScope"
      }
    }
  ],
  "created_by": "UtGYAXLklJd6S3dEHQXEJtKNsnk1",
  "lon": -53.3795
}
"""