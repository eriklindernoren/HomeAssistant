import sys, os
from wit import Wit
import speech_recognition as sr
from os import system


access_token = os.environ['WIT_TOKEN']


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    resp = response['text']
    print(response['text'])
    system('say -v Fred ' + resp)

def get_forecast(request):
    context = request['context']
    entities = request['entities']

    loc = first_entity_value(entities, 'location')
    if loc:
        context['forecast'] = 'sunny'
        if context.get('missingLocation') is not None:
            del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']

    return context


def get_team_prospect(request):
    context = request['context']
    entities = request['entities']

    team = first_entity_value(entities, 'team')
    if team:
        context['prospect'] = 'The ' + team + ' are looking really good.';
    else:
        if context.get('prospect') is not None:
            del context['prospect']
    return context

def exit(request):
    context = request['context']
    sys.exit(0)

actions = {
    'send': send,
    'getForecast': get_forecast,
    'getTeamProspects': get_team_prospect,
    'exit': exit
}


client = Wit(access_token=access_token, actions=actions)

while 1:
    try:
        context = {}
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        input = r.recognize_google(audio)
        print("Google thinks you said: " + input)
        session_id = 'session_id'
        new_context = client.run_actions(session_id, input, context)
        context = new_context
        print('The session state is now: ' + str(context))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


# try:
#     while 1:
#         with sr.Microphone() as source:
#             print("Say something!")
#             audio = r.listen(source)
#         input = r.recognize_wit(audio, key=access_token)
#         print("Wit.ai thinks you said: " + input)
#         session_id = '111'
#         context0 = {}
#         context1 = client.run_actions(session_id, input, context0)
#         print('The session state is now: ' + str(context1))
# except sr.UnknownValueError:
#     print("Wit.ai could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Wit.ai service; {0}".format(e))

