from pytlas import intent, training, translations
from datetime import datetime
import geocoder
from timezonefinderL import TimezoneFinder
from pytz import timezone
# This entity will be shared among training data since it's not language specific

help_en="""
The clock skill gives you time.

Example of sentences : 
  time please
  what's time in new york
  how does the clock skill work
"""
help_fr="""
La compétence horloge vous donne l'heure.

Exemple de phrase: 
  donne moi l'heure
  quelle heure est-il à paris
  comment fonctionne l'horloge
"""

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
%[help_clock]
  how does clock skill work
  give me help on clock skill

%[get_clock]
  what time is it?
  What's the time?
  Could you give me the time?
  Give me time.
  Time please.
  what time is it in @[location]?
  What's the time in @[location]?
""" + locations

@training('fr')
def fr_data(): return """
%[help_clock]
  comment fonctionne la compétence horloge
  donne moi de l'aide sur la compétence horloge

%[get_clock]
  Quelle heure est-il?
  Peux-tu me donner l'heure?
  Donne moi l'heure.
  Quelle heure est-il à @[location]?
  Peux-tu me donner l'heure qu'il est à @[location]?
  Donne moi l'heure qu'il est à @[location]?
""" + locations

@translations('fr')
def fr_translations(): return {
#  '%I:%M %p':'%H:%M',
  'It\'s {}': 'Il est {}',
  'It\'s {0} in {1}': 'A {1}, il est actuellement {0}',
  'Hummm! It seems {0} doesn\'t exists as city name': 'Hmmmm! Il semble que {0} ne soit pas le nom d\'une ville',
  'Hummm! I encountered an error during {0} information gathering': 'Hmmmm! J\'ai des difficultés pour récuperer les données concernant {0}',
  'Hummm! I can\'t retrieve time zone information of {0}':'Hmmmm! Je ne parviens pas à récuperer les données de fuseau horaire pour {0}',
  help_en:help_fr
}

@intent('help_clock')
def on_help_clock(req):
  req.agent.answer(req._(help_en))
  return req.agent.done()


@intent('get_clock')
def on_clock(req):
  city = req.intent.slot('location').first().value
  if not city:
    current_time = datetime.now().time()
    #resp = req._('It\'s {}').format(current_time.strftime(req._('%I:%M %p')))
    resp = req._('It\'s {}').format(req._d(current_time, time_only=True))
    req.agent.answer(resp)
    return req.agent.done()
  else:
    try:
      g = geocoder.osm(city)
      if not g:
        resp = req._('Hummm! It seems {0} doesn\'t exists as city name').format(city)
        req.agent.answer(resp)
        return req.agent.done()
    except:
        resp = req._('Hummm! I encountered an error during the city information gathering')
        req.agent.answer(resp)
        return req.agent.done()
    tf = TimezoneFinder()
    tzStr = tf.timezone_at(lng=g.lng, lat=g.lat)
    if tzStr == '':
        resp = req._('Hummm! I can\'t retrieve time zone information of {0}').format(city)
        req.agent.answer(resp)
        return req.agent.done()
    tzObj = timezone(tzStr)
    current_time = datetime.now(tzObj)
    #resp = req._('It\'s {0} in {1}').format(current_time.strftime(req._('%I:%M %p'), city)
    resp = req._('It\'s {0} in {1}').format(req._d(current_time, time_only=True), city)
  req.agent.answer(resp)
  return req.agent.done()