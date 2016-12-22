from pyicloud import PyiCloudService
import os, math
from datetime import datetime, timedelta

ICLOUD_MAIL = os.environ['ICLOUD_MAIL']
ICLOUD_PSWD = os.environ['ICLOUD_PSWD']

class Calendar(object):
	def __init__(self):
		api = PyiCloudService(ICLOUD_MAIL, ICLOUD_PSWD)
		api.calendar.refresh_client()
		from_dt = datetime.now()
		to_dt = from_dt + timedelta(days=30)
		event_day =  api.calendar.events(from_dt, to_dt)
		self._calendar = self.setup_calendar(event_day)

	def setup_calendar(self, calendar):
		events = []
		for event in calendar:
			title = event['title']
			location = event['location']
			date = event['startDate'][0]
			hour = str(event['startDate'][4])
			hour = "0" + hour if len(hour)==1 else hour
			minute = str(event['startDate'][5])
			minute = "0" + minute if len(minute)==1 else minute
			start_time = "%s-%s:%s" % (date, hour, minute)
			duration = event['duration']
			events.append({'title':title, 'location':location, 'start_time':start_time, 'duration': duration})
		return sorted(events, key=lambda k: k['start_time'])

	def get_events(self, date):
		events = []
		for event in self._calendar:
			_date = event['start_time'].split("-")[0]
			if date == _date:
				events.append(event)
			if _date > date:
				break
		return events

	def get_next_event(self):
		return self._calendar[0]
