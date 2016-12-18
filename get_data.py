# -*- coding: utf-8 -*-
import requests, os, json, feedparser, sys
from pytz import timezone
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

SPORTS_FEED_USER = "eriklindernoren"
SPORTS_FEED_PSWD = os.environ['SPORTS_FEED_PSWD']


class RemoteData(object):
    def __init__(self, weather_api_token, news_country_code='us'):
        self.news_country_code = news_country_code
        self.weather_api_token = weather_api_token
        self.geolocator = Nominatim()
        self.last_score = {}

    def find_weather(self, time, location=None, request_type="currently"):

        forecasts = {
            "minutely"  : "minutely_forecast",
            "hourly"    : "hourly_forecast",
            "daily"     : "daily_forecast",
            "currently" : "current_forecast"
        }

        if location:
            loc_obj = self.geolocator.geocode(location)
            lat = loc_obj.latitude
            lon = loc_obj.longitude
        else:
            loc_obj = self.get_location()
            lat = loc_obj['lat']
            lon = loc_obj['lon']
        time_obj = time

        units = 'si'
        request_types = ['minutely','currently','hourly','daily','alerts','flags']
        request_types.remove(request_type)

        exclude = ','.join(request_types)[:-1]

        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s,%s?exclude=%s&units=%s" % (self.weather_api_token, lat, lon, time_obj, exclude, units)
        r = requests.get(weather_req_url)
        weather_json = json.loads(r.text)

        forecast_request = forecasts[request_type]

        if forecast_request == "current_forecast":
            apparent_temp = weather_json[request_type]['apparentTemperature']
            temperature = weather_json[request_type]['temperature']
            summary = weather_json[request_type]['summary']
            return {'forecast_type': 'current', 'location': location, 'apparent_temperature': apparent_temp, 'temperature': temperature, 'summary': summary}
        elif forecast_request == "daily_forecast":
            summary = weather_json[request_type]['data'][0]['summary']
            temp_min = weather_json[request_type]['data'][0]['temperatureMin']
            temp_max = weather_json[request_type]['data'][0]['temperatureMax']
            return {'forecast_type': 'day', 'location': location, 'summary': summary, 'temp_min': temp_min, 'temp_max': temp_max}
        elif forecast_request == "hourly_forecast":
            hour = int(time_obj.split('T')[1].split(':')[0])
            temperature = weather_json[request_type]['data'][hour]['temperature']
            summary = weather_json[request_type]['data'][hour]['summary']
            return {'forecast_type': 'hour', 'location': location, 'summary': summary, 'temperature': temperature} 
        
        return {}

    def get_score(self, game_date, team="Celtics"):

        season = "2016-2017-regular"
        format = "json"

        home_team = ""
        home_score = 0
        away_team = ""
        away_score = 0
        finished = False

        if game_date:
            eastern_date = game_date - timedelta(hours=6)
            date = str(eastern_date).split(" ")[0].replace("-", "")
            games_url = "https://www.mysportsfeeds.com/api/feed/pull/nba/%s/scoreboard.%s?fordate=%s" % (season, format, date)
            r = requests.get(games_url, auth=(SPORTS_FEED_USER, SPORTS_FEED_PSWD))
            game_json = json.loads(r.text)

            games = game_json['scoreboard']['gameScore']
            if not games:
                return None

            for game in games:
                if game['game']['homeTeam']['Name'] == team or game['game']['awayTeam']['Name'] == team:
                    home_team = game['game']['homeTeam']['Name']
                    home_score = int(game['homeScore'])
                    away_team = game['game']['awayTeam']['Name']
                    away_score = int(game['awayScore'])
                    finished = (game["isCompleted"] == "true")
        else:
            counter = 2
            d = datetime.now()
            # Check the last three days
            while home_team == "" and counter > 0:
                d -= timedelta(days=1)
                date = str(d).split(" ")[0].replace("-", "")
                games_url = "https://www.mysportsfeeds.com/api/feed/pull/nba/%s/scoreboard.%s?fordate=%s" % (season, format, date)
                r = requests.get(games_url, auth=(SPORTS_FEED_USER, SPORTS_FEED_PSWD))
                game_json = json.loads(r.text)

                games = game_json['scoreboard']['gameScore']
                if not games:
                    return None

                for game in games:
                    if game['game']['homeTeam']['Name'] == team or game['game']['awayTeam']['Name'] == team:
                        home_team = game['game']['homeTeam']['Name']
                        home_score = int(game['homeScore'])
                        away_team = game['game']['awayTeam']['Name']
                        away_score = int(game['awayScore'])
                        finished = (game["isCompleted"] == "true")
                        break

                counter -= 0

        if home_team == "":
            return None
        
        score_data = {'home_team': home_team, 'home_score': home_score, 'away_team': away_team, 'away_score': away_score, 'finished': finished}
        print score_data

        self.last_score = score_data

        return score_data

    def get_location(self):
        location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
        r = requests.get(location_req_url)
        location_obj = json.loads(r.text)

        lat = location_obj['latitude']
        lon = location_obj['longitude']

        return {'lat': lat, 'lon': lon}

    def get_ip(self):
        ip_url = "http://jsonip.com/"
        req = requests.get(ip_url)
        ip_json = json.loads(req.text)
        return ip_json['ip']

    def get_map_url(self, location, map_type=None):
        if map_type == "satellite":
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=satellite&format=png" % location
        elif map_type == "terrain":
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=terrain&format=png" % location
        elif map_type == "hybrid":
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=hybrid&format=png" % location
        else:
            return "http://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=13&scale=false&size=1200x600&maptype=roadmap&format=png" % location

    def get_news(self):
        ret_headlines = []
        feed = feedparser.parse("https://news.google.com/news?ned=%s&output=rss" % self.news_country_code)

        for post in feed.entries[0:5]:
            ret_headlines.append(post.title)

        return ret_headlines

    def get_holidays(self):
        today = datetime.now()
        r = requests.get("http://kayaposoft.com/enrico/json/v1.0/?action=getPublicHolidaysForYear&year=%s&country=swe" % today.year)
        holidays = json.loads(r.text)

        return holidays

