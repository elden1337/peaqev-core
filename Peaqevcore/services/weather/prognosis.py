from datetime import datetime
import logging
from ...models.weather.weather_object import WeatherObject

_LOGGER = logging.getLogger(__name__)


class WeatherPrognosis:
    def __init__(self):
        self.prognosis_list = list[WeatherObject]

    def set_prognosis(self, import_list: list):
        ret = []

        for i in import_list:
            ret.append(
                WeatherObject(
                    _DTstr=i["datetime"], 
                    WeatherCondition=i["condition"], 
                    Temperature=i["temperature"], 
                    Wind_Speed=i["wind_speed"], 
                    Wind_Bearing=i["wind_bearing"], 
                    Precipitation_Probability=i["precipitation_probability"], 
                    Precipitation=i["precipitation"])
            )
        self.prognosis_list = ret

    def make_hvac_prognosis(self, current_temperature: float) -> list[PrognosisExportModel]:
        ret = []
        now = datetime.now()
        thishour = datetime(now.year, now.month, now.day, now.hour, 0, 0)
        
        valid_progs = [p for idx, p in enumerate(self.prognosis_list) if p.DT >= thishour]
        if len(valid_progs) == 0:
          _LOGGER.debug("No prognosis available")
          return []
        
        corrected_temp_delta = 0

        for p in valid_progs:
          c = p.DT - thishour
          if c.seconds == 0:
            corrected_temp_delta = round(current_temperature - p.Temperature,2)
            continue
          if 3600 <= c.seconds <= 21600:
            #correct the temp
            temp = round(p.Temperature + corrected_temp_delta / int(c.seconds/3600),1)
          else:
            temp = p.Temperature
          hourdiff = int(c.seconds/3600)
          hour_prognosis = PrognosisExportModel(p.Temperature, temp, self.correct_temperature_for_windchill(temp, p.Wind_Speed), p.DT, hourdiff)
          ret.append(hour_prognosis)
        return ret
  
    def correct_temperature_for_windchill(self, temp: float, windspeed: float) -> float:
        windspeed_corrected = windspeed
        ret =13.12 + (0.6215 * temp)-(11.37*windspeed_corrected**0.16) + (0.3965 * temp * windspeed_corrected**0.16) 
        return round(ret,1)

        #how hot is it outside?
        #what is the prognosis?
        #what kind of weatherenum is it (add/remove based on that)


test_input = [
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-19T18:00:00+00:00",
    "wind_bearing": 41.3,
    "temperature": 1.2,
    "wind_speed": 20.2,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-19T19:00:00+00:00",
    "wind_bearing": 44.5,
    "temperature": 0.9,
    "wind_speed": 19.4,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-19T20:00:00+00:00",
    "wind_bearing": 45.1,
    "temperature": 0.7,
    "wind_speed": 19.4,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-19T21:00:00+00:00",
    "wind_bearing": 47.3,
    "temperature": 0.5,
    "wind_speed": 19.1,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-19T22:00:00+00:00",
    "wind_bearing": 50,
    "temperature": 0.3,
    "wind_speed": 18.7,
    "precipitation": 0
  },
  {
    "condition": "sunny",
    "precipitation_probability": 0,
    "datetime": "2022-11-19T23:00:00+00:00",
    "wind_bearing": 50.2,
    "temperature": 0,
    "wind_speed": 16.6,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T00:00:00+00:00",
    "wind_bearing": 37.2,
    "temperature": -0.4,
    "wind_speed": 14.4,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T01:00:00+00:00",
    "wind_bearing": 45.8,
    "temperature": -0.7,
    "wind_speed": 13.7,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T02:00:00+00:00",
    "wind_bearing": 39.6,
    "temperature": -0.8,
    "wind_speed": 14,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T03:00:00+00:00",
    "wind_bearing": 41.9,
    "temperature": -0.5,
    "wind_speed": 15.8,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T04:00:00+00:00",
    "wind_bearing": 40.8,
    "temperature": -0.2,
    "wind_speed": 15.5,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T05:00:00+00:00",
    "wind_bearing": 46.3,
    "temperature": -0.1,
    "wind_speed": 13.7,
    "precipitation": 0
  },
  {
    "condition": "partlycloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T06:00:00+00:00",
    "wind_bearing": 48.7,
    "temperature": -0.2,
    "wind_speed": 12.6,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T07:00:00+00:00",
    "wind_bearing": 52.8,
    "temperature": -0.3,
    "wind_speed": 13.3,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 1.1,
    "datetime": "2022-11-20T08:00:00+00:00",
    "wind_bearing": 49.6,
    "temperature": 0,
    "wind_speed": 13.3,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 0.9,
    "datetime": "2022-11-20T09:00:00+00:00",
    "wind_bearing": 44.8,
    "temperature": 0.7,
    "wind_speed": 12.6,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 0,
    "datetime": "2022-11-20T10:00:00+00:00",
    "wind_bearing": 42.2,
    "temperature": 1.3,
    "wind_speed": 14.4,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 0.1,
    "datetime": "2022-11-20T11:00:00+00:00",
    "wind_bearing": 43,
    "temperature": 1.5,
    "wind_speed": 14.8,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 1,
    "datetime": "2022-11-20T12:00:00+00:00",
    "wind_bearing": 43.5,
    "temperature": 1.6,
    "wind_speed": 13,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 11.8,
    "datetime": "2022-11-20T13:00:00+00:00",
    "wind_bearing": 37.9,
    "temperature": 1.5,
    "wind_speed": 13.3,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 29.2,
    "datetime": "2022-11-20T14:00:00+00:00",
    "wind_bearing": 24.2,
    "temperature": 1.1,
    "wind_speed": 12.6,
    "precipitation": 0
  },
  {
    "condition": "cloudy",
    "precipitation_probability": 44.5,
    "datetime": "2022-11-20T15:00:00+00:00",
    "wind_bearing": 9.6,
    "temperature": 0.8,
    "wind_speed": 11.2,
    "precipitation": 0
  },
  {
    "condition": "snowy",
    "precipitation_probability": 57.4,
    "datetime": "2022-11-20T16:00:00+00:00",
    "wind_bearing": 357.4,
    "temperature": 0.5,
    "wind_speed": 10.8,
    "precipitation": 0.2
  },
  {
    "condition": "snowy",
    "precipitation_probability": 68.4,
    "datetime": "2022-11-20T17:00:00+00:00",
    "wind_bearing": 349.2,
    "temperature": 0.2,
    "wind_speed": 10.1,
    "precipitation": 0.3
  }
]


w = WeatherPrognosis()
w.set_prognosis(test_input)

prog = w.make_hvac_prognosis(1.6)

for p in prog:
  print(p)

# for w in w.prognosis_list:
#     print(w)


#time_str = "2022-11-17T16:00:00+00:00"





