import speech_recognition as sr
from os import system
class AudioHandler(object):
	def __init__(self, energy_threshold):
		self.mic = sr.Microphone()
		self.recognizer = sr.Recognizer()
		self.recognizer.energy_threshold = energy_threshold

	def speak(self, message):
		system('say -v Fred ' + message)

	def get_audio_as_text(self):
		with self.mic as source:
			print("Say something!")
			audio = self.recognizer.listen(source)
			return self.recognizer.recognize_google(audio)