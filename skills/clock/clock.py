from pytlas import intent, training, translations
from datetime import datetime
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
  'It\'s %s': 'Il est %s'
}

@intent('get_clock')
def on_clock(req):
  city = req.intent.slot('location').first().value
  if not city:
    city = "local"
  current_time = time.now()
  req.agent.answer(req._('It\'s %s') % current_time.strftime('%c'))
  return req.agent.done()