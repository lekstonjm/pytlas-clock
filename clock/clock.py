from pytlas import intent, training, translations, Card
from datetime import datetime
from dateutil.parser import parse as dateParse 
import requests, pytz

# This entity will be shared among training data since it's not language specific
locations = """
@[location]
  los angeles
  paris
  rio de janeiro
  tokyo
  london
  tel aviv
  new york
  saint-étienne du rouvray
"""

@training('en')
def en_data(): return """
%[get_clock]
  what time is it?
  What's the time?
  Could you give me the time?
  what time is it in @[location]?
  What's the time in @[location]?
""" + locations

@training('fr')
def fr_data(): return """
%[get_clock]
  Quelle heure est-il?
  Peux-tu me donner l'heure?
  donne moi l'heure?
  Quelle heure est-il à @[location]?
  Peux-tu me donner l'heure qu'il est à @[location]?
  donne moi l'heure qu'il est à @[location]?
""" + locations

@translations('fr')
def fr_translations(): return {
  'It is %s': 'Il est %s'
}

@intent('get_clock')
def on_clock(req):

  city = req.intent.slot('location').first().value
  if not city:
    city = "local"
    #return req.agent.ask('location', req._('For where?'))

  # Here we try to determine the grain of the given date slot
  # to give better targeted results to the user
  date_meta = date_slot.meta.get('value', {})
  date_from = date_meta.get('from')
  date_to = date_meta.get('to')

  if date_from and date_to:
    date = (dateParse(date_from), dateParse(date_to))

  forecasts = fetch_forecasts_for(city, date, date_meta.get('grain'), appid, req.lang, units)

  if len(forecasts) > 0:
    req.agent.answer(req._('Here what I found for %s!') % city, cards=[create_forecast_card(req, d, units) for d in forecasts])
  else:
    req.agent.answer(req._('No results found for %s') % city)

  return req.agent.done()

def create_forecast_card(req, data, unit):
  w = data['weather'][0]

  icon = emojis_map.get(w['icon'][:-1])
  desc = w['description'].capitalize()
  temps = '{min}{unit} - {max}{unit}'.format(unit=units_map.get(unit), min=int(data['main']['temp_min']), max=int(data['main']['temp_max']))

  return Card('%s %s' % (icon, desc), temps, req._d(data['date']))

def fetch_forecasts_for(city, date, grain, appid, lang, units):
  payload = {
    'q': city,
    'units': units,
    'lang': lang,
    'appid': appid,
  }
  
  r = requests.get('https://api.openweathermap.org/data/2.5/forecast', params=payload)

  if not r.ok:
    return []

  result = []

  for data in r.json().get('list', []):
    # TODO check timezones

    parsed_date = dateParse(data.get('dt_txt')).replace(tzinfo=pytz.UTC)
    data['date'] = parsed_date # Keep it in the data dict for the card

    if isinstance(date, tuple):
      if parsed_date >= date[0] and parsed_date <= date[1]:
        result.append(data)
    else:
      # Returns the first one superior, that's the best we can do
      if grain == 'Hour' and parsed_date >= date:
        return [data]
      
      if parsed_date.date() == date.date():
        result.append(data)

  return result
