# -*- coding: utf-8 -*-
from ics import Calendar
from urllib2 import urlopen # import requests
import os, math
from datetime import datetime, timedelta

UNI_ICS_URL = os.environ['UNI_ICS_URL']

class UniversityCalendar(object):
	def __init__(self):
		url = UNI_ICS_URL
		c = Calendar(urlopen(url).read().decode('utf-8'))
		self.events = {}
		for event in c.events:
			event_name = event.name.encode('utf-8')
			name = event_name.split(", ")[0]

			type = ""
			if "FÖ" in event_name:
				type = "lecture"
			elif "SE" in event_name:
				type = "seminar"
			elif "LA" in event_name:
				type = "lab"
			elif "RE" in event_name:
				type = "presentation"
			elif "LE" in event_name:
				type = "class"
			
			location = ""
			if event.location:
				location = event.location.encode('utf-8').split(" : ")[1]

			date = str(event.begin).split("T")[0]
			begin_time = ":".join(str(event.begin).split("T")[1].split(":")[0:2])
			end_time = ":".join(str(event.end).split("T")[1].split(":")[0:2])
			if date not in self.events:
				self.events[date] = []
			print "Event - name: %s, location: %s, type: %s, date: %s (%s - %s)" % (name, location, type, date, begin_time, end_time)
			self.events[date].append({"name": name, "location": location, "type": type, "date": date, "begin": begin_time, "end": end_time})

	def get_events(self, date):
		event_list = None
		if date in self.events:
			event_list = sorted(self.events[date], key=lambda k: k['begin'])
		return event_list

	def get_next_event(self):
		event = None
		for i in range(31):
			day = str(datetime.now() + timedelta(days=i)).split(" ")[0]
			events = self.get_events(day)
			if events:
				event = events[0]
				break
		return event
