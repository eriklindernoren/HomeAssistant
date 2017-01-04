import sys
from _ical import ICalendar
from _uni_cal import UniversityCalendar

class Calendar(object):
	def __init__(self):
		# Fetch updated calendars
		print "Updating calendars"
		self.uni_cal = UniversityCalendar()
		print "\t- University schedule finished"
		self.ical = ICalendar()
		print "\t- iCloud calendar finished"
		print "Done."

	def get_events(self, date):
		uni_events = self.uni_cal.get_events(date)
		my_events = self.ical.get_events(date)
		events = []
		# Add events from personal and uni calendar
		if uni_events:
			events += uni_events
		if my_events:
			events += my_events
		# Sort the events by their start times
		return sorted(events, key=lambda k: k['begin'])

	def get_next_event(self):
		uni_event = self.uni_cal.get_next_event()
		icloud_event = self.ical.get_next_event()
		event = None
		# If there are both uni and personal events scheduled on the same date
		# => compare when they begin and return the earlies event
		if uni_event and icloud_event:
			if icloud_event["date"] == uni_event["date"]:
				if icloud_event["begin"] <= uni_event['begin']:
					event = icloud_event
				else:
					event = uni_event
			elif icloud_event["date"] < uni_event["date"]:
				event = icloud_event
			else:
				event = uni_event
		elif uni_event:
			event = uni_event
		elif icloud_event:
			event = icloud_event
		return event