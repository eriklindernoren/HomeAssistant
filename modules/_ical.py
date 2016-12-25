from pyicloud import PyiCloudService
import os, math
from datetime import datetime, timedelta

ICLOUD_MAIL = os.environ['ICLOUD_MAIL']
ICLOUD_PSWD = os.environ['ICLOUD_PSWD']

class ICalendar(object):
	def __init__(self):
		self.api = PyiCloudService(ICLOUD_MAIL, ICLOUD_PSWD)
		self.api.calendar.refresh_client()
		self.events = None
		self.setup_calendar(datetime.now(), datetime.now() + timedelta(days=30))

	def setup_calendar(self, date_from, date_to):
		events = {}
		for event in self.api.calendar.events(date_from, date_to):
			title = event['title']
			location = event['location']
			# Date
			date = "%s-%s-%s" % (str(event['startDate'][0])[0:4], str(event['startDate'][0])[4:6], str(event['startDate'][0])[6:8])
			# Start time
			hour = str(event['startDate'][4])
			hour = "0" + hour if len(hour)==1 else hour
			minute = str(event['startDate'][5])
			minute = "0" + minute if len(minute)==1 else minute
			begin = "%s:%s" % (hour, minute)
			# End time
			hour = str(event['endDate'][4])
			hour = "0" + hour if len(hour)==1 else hour
			minute = str(event['endDate'][5])
			minute = "0" + minute if len(minute)==1 else minute
			end = "%s:%s" % (hour, minute)
			# duration
			duration = event['duration']
			# Add to events
			if not date in events:
				events[date] = []
			events[date].append({'title':title, 'date': date, 'location':location, 'begin':begin, 'end':end, 'duration': duration})
		self.events = events

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
