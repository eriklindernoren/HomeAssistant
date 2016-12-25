import sys
from _ical import ICalendar
from _uni_cal import UniversityCalendar

class Calendar(object):
	def __init__(self):
		self.uni_cal = UniversityCalendar()
		self.ical = ICalendar()

	def get_events(self, date):
		uni_events = self.uni_cal.get_events(date)
		my_events = self.ical.get_events(date)
		events = []
		if uni_events:
			events += uni_events
		if my_events:
			events += my_events
		return sorted(events, key=lambda k: k['begin'])

	def get_next_event(self):
		uni_event = self.uni_cal.get_next_event()
		my_event = self.ical.get_next_event()
		event = None
		if uni_event and my_event:
			if my_event["date"] == uni_event["date"]:
				if my_event["begin"] <= uni_event:
					event = my_event
				else:
					event = uni_event
			elif my_event["date"] < uni_event["date"]:
				event = my_event
			else:
				event = uni_event
		elif uni_event:
			event = uni_event
		elif my_event:
			event = my_event
		return event