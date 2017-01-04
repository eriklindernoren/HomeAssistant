# -*- coding: utf-8 -*-
import sys, os, signal, datetime, threading, logging, time, uuid
from flask import Flask, render_template, jsonify, request, url_for
from tellcore.telldus import TelldusCore
from wit import Wit
from os import system
sys.path.insert(0, "./modules/")
from get_data import RemoteData
from audio_handler import AudioHandler
from nlg import NLG
from cal import Calendar


core = TelldusCore()

devices = {}
for device in core.devices():
    devices[device.name] = device

devices_in_room = {
    "bedroom": ["sovrum"],
    "living room": ["skrivbord"],
    "office": ["skrivbord"],
}

device_translation = {
    "desk lamp": "skrivbord",
    "bed lamp": "sovrum"
}

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

WIT_TOKEN = os.environ['WIT_TOKEN']
DARKSKY_TOKEN = os.environ['DARKSKY_TOKEN']

NAME = "Erik"

class Alfred():
    def __init__(self):
        self.nlg = NLG(user_name=NAME)
        self.remote_data = RemoteData(weather_api_token=DARKSKY_TOKEN)
        self.audio_handler = AudioHandler(debug=True)
        #self.calendar = Calendar()
        self.calendar = None
        self.session_id = uuid.uuid1()
        self.context = {}
        self.prev_ai_message = ""
        self.ai_message = " - "
        self._active_alarms = []
        self.active = False     # When the user has activated Alfred

    def close(self):
        self.nlg.close()
        sys.exit(0)

    def get_ai_message(self):
        message = self.ai_message
        return message

    def get_alarms(self):
        alarms = self._active_alarms
        return alarms

    def _active_timeout(self, signum, frame):
        print "Timeout..."
        del self.context['active']
        return self.context

    def _first_entity_value(self, entities, entity):
        if entity not in entities:
            return None
        if 'value' in entities[entity][0]:
            val = entities[entity][0]['value']
            return val['value'] if isinstance(val, dict) else val
        elif 'values' in entities[entity][0]:
            return {"from": entities[entity][0]["from"]["value"], "to": entities[entity][0]["to"]["value"]}
        else:
            return None
        
    def _confident(self, entities):
        if not entities:
            return False

        print entities
        if not "Intent" in entities:
             # Trust that entities confidence is high
            return True

        intent = entities['Intent'][0]['value']
        confidence = float(entities['Intent'][0]['confidence'])
        print "Confidence (%s): %s" % (intent, confidence)

        return (confidence > 0.8)
        
        



    def _if_wake_alfred(self, message):
        if "Alfred" in message:
            self.active = True

    def _converse(self, message):
        # print ""
        # print "Message:", message
        # print "Context:", self.context
        # print "Session-id:", self.session_id
        # print ""
        new_context = self.client.run_actions(self.session_id, message, self.context)
        self.context = new_context
        print('The session state is now: ' + str(self.context))
        


    # --------
    # ACTIONS
    # --------

    def _send(self, request, response):
        message = response['text']
        if message != self.prev_ai_message:
            self.ai_message = message
            print "Alfred:", message
        self.prev_ai_message = message

    def _get_forecast(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        weather_request = "currently"

        loc = self._first_entity_value(entities, 'location')

        time = self._first_entity_value(entities, 'datetime')
        if not time:
            time = datetime.datetime.now()
        else:
            w_type = entities[u'datetime'][0][u'grain']
            if w_type == "hour":
                weather_request = "hourly"
            elif w_type == "second":
                weather_request = "minutely"
            elif w_type == "day":
                weather_request = "daily"

        time_query = str(time).split('.')[0].replace(' ', 'T')    # Remove timezone

        encoded_date_obj = datetime.datetime.strptime(time_query.split('.')[0], '%Y-%m-%dT%H:%M:%S')

        # search_phrase = self.nlg.searching()
        # self.ai_message = search_phrase
        weather_obj = self.remote_data.find_weather(time_query, loc, weather_request)

        context = {}
        context['forecast'] = self.nlg.weather(weather_obj, encoded_date_obj)

        return context

    def _get_score(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        team = self._first_entity_value(entities, 'team')
        date = self._first_entity_value(entities, 'datetime')
        if date != None:
            if isinstance(date, dict):
                date = date["from"]
            date = str(date).split('.')[0].replace(' ', 'T')
            date = datetime.datetime.strptime(date.split('.')[0], '%Y-%m-%dT%H:%M:%S')

        # search_phrase = self.nlg.searching()
        # self.ai_message = search_phrase

        score_obj = self.remote_data.get_score(date, team)

        context = {}
        if not score_obj:
            self.ai_message = "Sorry. I could not find any scores matching your request."
        else:    
            context['score'] = self.nlg.score(score_obj)

        return context

    def _get_news(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        # team = self._first_entity_value(entities, 'team')

        # time_query = str(time).split('.')[0].replace(' ', 'T')    # Remove timezone
        # encoded_date_obj = datetime.datetime.strptime(time_query.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        
        news_obj = self.remote_data.get_news()
        context = {}
        self.nlg.news("past")
        interest = self.nlg.article_interest(news_obj)
        if interest is not None:
            context['news'] = interest

        return context


    def _greeting(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        by_name = False
        ai = self._first_entity_value(entities, 'ai_entity')
        if ai:
            by_name = True

        context = {}
        context['greeting'] = self.nlg.greet(by_name)

        return context

    def _joke(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        context = {}
        context['joke'] = self.nlg.joke()

        return context

    def _status(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        context = {}
        context['status'] = self.nlg.personal_status()

        return context

    def _appreciation_response(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        context = {}
        context['appreciation_response'] = self.nlg.appreciation()

        return context

    def _set_alarm_clock(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        datetime = self._first_entity_value(entities, 'datetime')

        context = {}
        if not datetime:
            context['alarm_time_missing'] = self.nlg.alarm_info(None, None)
            print "Alarm: %s" % (context)
            return context
        
        date = datetime.split("T")[0]
        time = ":".join(datetime.split("T")[1].split(".")[0].split(":")[:-1])
        self._active_alarms.append({"date": date, "time": time})
        print "date: %s, time: %s" % (date, time)
        context['alarm_confirmation'] = self.nlg.alarm_info(date, time)

        print "Alarm: %s" % (context)
        return context

    def _manage_lights(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        off_on = self._first_entity_value(entities, 'off_on')
        room = self._first_entity_value(entities, 'location')
        lamp = self._first_entity_value(entities, 'lamp')

        context = {}
        if room:
            if room in devices_in_room:
                context['lights_confirmation'] = self.nlg.lights_confirmation("room", room, off_on)
                for key in devices_in_room[room]:
                    if off_on == "on":
                        devices[key].turn_on()
                    else:
                        devices[key].turn_off()
            else:
                context['lights_confirmation'] = self.nlg.lights_confirmation("room", None, None)
        elif lamp:
            if lamp in device_translation:
                key = device_translation[lamp]
                context['lights_confirmation'] = self.nlg.lights_confirmation("lamp", lamp, off_on)
                if off_on == "on":
                    devices[key].turn_on()
                else:
                    devices[key].turn_off()
            else:
                context['lights_confirmation'] = self.nlg.lights_confirmation("lamp", None, None)
        else:
            if not off_on:
                off_on = "on"
            context['lights_confirmation'] = self.nlg.lights_confirmation("all", None, off_on)
            for key in devices.keys():
                if off_on == "on":
                    devices[key].turn_on()
                else:
                    devices[key].turn_off()

        return context

    def _acknowledgement(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        context = {}
        context['acknowledge_response'] = self.nlg.acknowledge()

        return context

    def _get_next_event(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        event = self.calendar.get_next_event()
        context = {}
        context['next_event'] = self.nlg.next_event(event)

        return context

    def _get_events(self, request):
        entities = request['entities']
        context = {}

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        datetime = self._first_entity_value(entities, 'datetime')

        if not datetime:
            context['events_missing'] = "What date do you want me to check?"
            return context

        date = datetime.split("T")[0]

        events = self.calendar.get_events(date)
        context['events'] = self.nlg.events(events)

        return context


    def _identification(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        context = {}
        context['identification'] = self.nlg.identification()

        return context

    def _sleep(self, request):
        entities = request['entities']
        context = request['context']

        if not self._confident(entities):
            self.ai_message = self.nlg.clueless()
            return context

        self.active = False
        context = {}
        context["bye"] = self.nlg.goodbye()
        return context


# ---------
# START BOT
# ---------

alfred = Alfred()
alfred.actions = {
            'send': alfred._send,
            'getForecast': alfred._get_forecast,
            'goToSleep': alfred._sleep,
            'greeting': alfred._greeting,
            'getJoke': alfred._joke,
            'getStatus': alfred._status,
            'getAppreciationResponse': alfred._appreciation_response,
            'getAcknowledgement': alfred._acknowledgement,
            'getScore': alfred._get_score,
            'getNews': alfred._get_news,
            'identification': alfred._identification,
            'setAlarm': alfred._set_alarm_clock,
            'manageLights': alfred._manage_lights,
            'getNextEvent': alfred._get_next_event,
            'getEvents': alfred._get_events
        }

alfred.client = Wit(access_token=WIT_TOKEN, actions=alfred.actions)  

# Generate the landing page
@app.route("/")
def index():
    return render_template('index.html')

# Receives the user input => generates response
@app.route('/_communication', methods= ['GET'])
def handle_text():
    input_text = request.args.get('text', 0, type=str)
    print "User message: " + input_text
    alfred._converse(input_text)
    ai_message = alfred.get_ai_message()
    print "AI message: " + ai_message
    return jsonify(ai_message=ai_message)

if __name__ == "__main__":
	# Set host address so that the server is accessible network wide
    app.run(host='0.0.0.0', port="5050")


