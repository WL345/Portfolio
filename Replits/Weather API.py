import json
import requests
import sys

city = input("What city do you want the weather for?\n")

LocationKeyURL = requests.get(f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey=***No API key for you!***&q={city}").json()

LocKey = LocationKeyURL[0]["Key"]
type = input("What do you want? Forecast (1)\n")

# Forecast
if type == "1":
  time = input("Daily or Hourly weather?\n")
  if time.lower() == "daily":
    AmtDay = input("How many days? (1, 5)\n")
    print()
    if AmtDay in ["1", "5"]:
      Data = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/daily/{AmtDay}day/{LocKey}?apikey=***No API key for you!***").json()
        # A very long way to say the date, headlines, and temperatures
      for i in range(int(AmtDay)):
        if i == 0:
          print(f'''Today, {Data["Headline"]["EffectiveDate"][5]}{Data["Headline"]["EffectiveDate"][6]}/{Data["Headline"]["EffectiveDate"][8]}{Data["Headline"]["EffectiveDate"][9]}/{Data["Headline"]["EffectiveDate"][2]}{Data["Headline"]["EffectiveDate"][3]},
    {Data["Headline"]["Text"]}. Anticipate a high of {Data["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]}°F and a low of {Data["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]}°F.''')
          print()
      sources = Data["DailyForecasts"][0]["Sources"]
      sources = ", ".join(sources)
      print(f'Sources: {sources}')  # Cites all sources w/ commas, Source1, Source2, etc

    else:
      print("1 or 5 not inputted")
  elif time.lower() == "hourly":
    AmtHour = input("How many hours? (1, 12)\n")
    if AmtHour in ["1", "12"]:
      Data = requests.get(f"http://dataservice.accuweather.com/forecasts/v1/hourly/{AmtHour}hour/{LocKey}?apikey=***No API key for you!***")
      print(json.dumps(Data.json(), indent=2))
    else:
      print("1 or 12 not inputted")
