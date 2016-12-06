import sys, os, signal, datetime, threading, logging, time
from flask import Flask, render_template, jsonify, request
from wit import Wit
from os import system
from get_data import RemoteData
from audio_handler import AudioHandler
from nlg import NLG
import uuid


app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

WIT_TOKEN = os.environ['WIT_TOKEN']
DARKSKY_TOKEN = os.environ['DARKSKY_TOKEN']

NAME = "Erik"

class Alfred(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.nlg = NLG(user_name=NAME)
        self.remote_data_access = RemoteData(weather_api_token=DARKSKY_TOKEN)
        self.audio_handler = AudioHandler(debug=True)
        self.session_id = uuid.uuid1()
        self.context = {}
        self.last_ai_message = ""
        self.last_user_message = ""
        self.talking = False;
        self.active = True

    def close(self):
        self.nlg.close()
        sys.exit(0)

    def get_ai_message(self):
        message = self.last_ai_message
        return message

    def get_user_message(self):
        message = self.last_user_message
        return message

    def _active_timeout(self, signum, frame):
        print "Timeout..."
        del self.context['active']
        return self.context

    def _first_entity_value(self, entities, entity):
        if entity not in entities:
            return None
        val = entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def _if_wake_alfred(self, message):
        if "Alfred" in message:
            self.active = True

    def _converse(self, context, message):
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
        if not self.talking:
            self.last_ai_message = message
            print "Alfred:", message

    def _get_forecast(self, request):
        entities = request['entities']
        context = request['context']

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

        search_phrase = self.nlg.searching()
        self.last_ai_message = search_phrase
        weather_obj = self.remote_data_access.find_weather(time_query, loc, weather_request)

        context['forecast'] = self.nlg.weather(weather_obj, encoded_date_obj)

        return context

    def _get_score(self, request):
        entities = request['entities']
        context = request['context']

        team = self._first_entity_value(entities, 'team')

        # time_query = str(time).split('.')[0].replace(' ', 'T')    # Remove timezone
        # encoded_date_obj = datetime.datetime.strptime(time_query.split('.')[0], '%Y-%m-%dT%H:%M:%S')

        search_phrase = self.nlg.searching()
        self.last_ai_message = search_phrase

        score_obj = self.remote_data_access.get_score(team)

        # context['forecast'] = self.nlg.weather(weather_obj, encoded_date_obj)

        return context


    def _greeting(self, request):
        entities = request['entities']
        context = request['context']

        context['greeting'] = self.nlg.greet()

        return context

    def _joke(self, request):
        entities = request['entities']
        context = request['context']

        context['joke'] = self.nlg.joke()

        return context

    def _status(self, request):
        entities = request['entities']
        context = request['context']

        context['status'] = self.nlg.personal_status()

        return context

    def _appreciation_response(self, request):
        entities = request['entities']
        context = request['context']

        context['status'] = self.nlg.appreciation()

        return context

    def _acknowledgement(self, request):
        entities = request['entities']
        context = request['context']

        context['status'] = self.nlg.acknowledge()

        return context

    def _sleep(self, request):
        self.active = False
        context = {}
        context["bye"] = self.nlg.goodbye()
        return context


    # ---------
    # START BOT
    # ---------

    def run(self):

        self.actions = {
            'send': self._send,
            'getForecast': self._get_forecast,
            'goToSleep': self._sleep,
            'greeting': self._greeting,
            'getJoke': self._joke,
            'getStatus': self._status,
            'getAppreciationResponse': self._appreciation_response,
            'getAcknowledgement': self._acknowledgement,
            'getScore': self._get_score
        }
        self.client = Wit(access_token=WIT_TOKEN, actions=self.actions)        

        while 1:
            try:
                if not self.talking:
                    input_text = self.audio_handler.get_audio_as_text()
                    self._if_wake_alfred(input_text)
                    if self.active:
                        self.last_user_message = input_text
                        self._converse(self.context, input_text)
                else:
                    time.sleep(0.2)
            except Exception as e:
                continue


alfred = Alfred()

@app.route("/")
def startAlfred():
    return render_template('alfred.html')

@app.route('/_talking', methods= ['GET'])
def handleTalkingStatus():
    talking = request.args.get('talking', 0, type=int)
    talking = (talking == 1)
    alfred.talking = talking
    print "Talking set to:", talking
    return jsonify(success="true")

# @app.route('/_handle_text', methods= ['GET'])
# def handleText():
#     input_text = request.args.get('text', 0, type=str)
#     print input_text
#     alfred._if_wake_alfred(input_text, alfred.context)
#     if 'active' in alfred.context:
#         alfred.last_user_message = input_text
#         alfred._converse(alfred.context, input_text)
#     user_message = alfred.get_user_message()
#     ai_message = alfred.get_ai_message()
#     return jsonify(ai_message=ai_message, user_message=user_message)

@app.route('/_get_message', methods= ['GET'])
def getMessage():
    user_message = alfred.get_user_message()
    ai_message = alfred.get_ai_message()
    return jsonify(ai_message=ai_message, user_message=user_message)

if __name__ == "__main__":
    alfred.start()
    app.run()


