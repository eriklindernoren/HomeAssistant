import requests, os, json, feedparser, sys
from pytz import timezone
from datetime import datetime, timedelta

SPORTS_FEED_USER = "eriklindernoren"
# SPORTS_FEED_PSWD = os.environ['SPORTS_FEED_PSWD']
SPORTS_FEED_PSWD = "sportsfeed"


class RemoteData(object):
    def __init__(self, weather_api_token, news_country_code='us'):
        self.news_country_code = news_country_code
        self.weather_api_token = weather_api_token

    def find_weather(self, time, location=None, request_type="currently"):

        forecasts = {
            "minutely"  : "minutely_forecast",
            "hourly"    : "hourly_forecast",
            "daily"     : "daily_forecast",
            "currently" : "current_forecast"
        }

        loc_obj = location
        if not loc_obj:
            loc_obj = self.get_location()
        time_obj = time

        lat = loc_obj['lat']
        lon = loc_obj['lon']

        units = 'si'
        request_types = ['minutely','currently','hourly','daily','alerts','flags']
        request_types.remove(request_type)

        exclude = ','.join(request_types)[:-1]

        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s,%s?exclude=%s&units=%s" % (self.weather_api_token, lat, lon, time_obj, exclude, units)
        r = requests.get(weather_req_url)
        weather_json = json.loads(r.text)

        forecast_request = forecasts[request_type]

        if forecast_request == "current_forecast":
            temperature = int(weather_json[request_type]['temperature'])
            current_forecast = weather_json[request_type]['summary']
            return {'forecast_type': 'current', 'temperature': temperature, 'current_forecast': current_forecast}
        elif forecast_request == "daily_forecast":
            summary = weather_json[request_type]['data'][0]['summary']
            temp_min = weather_json[request_type]['data'][0]['temperatureMin']
            temp_max = weather_json[request_type]['data'][0]['temperatureMax']
            return {'forecast_type': 'day', 'summary': summary, 'temp_min': temp_min, 'temp_max': temp_max}
        elif forecast_request == "hourly_forecast":
            hour = int(time_obj.split('T')[1].split(':')[0])
            temperature = weather_json[request_type]['data'][hour]['temperature']
            summary = weather_json[request_type]['data'][hour]['summary']
            return {'forecast_type': 'hour', 'summary': summary, 'temperature': temperature} 
        
        return {}

    def get_score(self, team="Celtics"):

        team = team.capitalize()

        eastern_time = datetime.now()
        season = "2016-2017-regular"
        format = "json"

        counter = 2
        home_team = ""
        home_abbr = ""
        away_team = ""
        away_abbr = ""
        while home_abbr == "" and counter > 0:
            eastern_time -= timedelta(days=1)
            date = str(eastern_time).split(" ")[0].replace("-", "")
            games_url = "https://www.mysportsfeeds.com/api/feed/pull/nba/%s/daily_game_schedule.%s?fordate=%s" % (season, format, date)
            r = requests.get(games_url, auth=(SPORTS_FEED_USER, SPORTS_FEED_PSWD))
            game_json = json.loads(r.text)

            games = game_json['dailygameschedule']['gameentry']
            if not games:
                return None

            for game in games:
                if game['homeTeam']['Name'] == team or game['awayTeam']['Name'] == team:
                    home_team = game['homeTeam']['Name']
                    home_abbr = game['homeTeam']['Abbreviation']
                    away_team = game['awayTeam']['Name']
                    away_abbr = game['awayTeam']['Abbreviation']
                    break

            counter -= 0
        
        # Couldn't find any game played in the last three days
        if home_abbr == "":
            return None
        
        game_id = "%s-%s-%s" % (date, away_abbr, home_abbr)
        print game_id
        score_url = "https://www.mysportsfeeds.com/api/feed/pull/nba/%s/game_boxscore.%s?gameid=%s&teamstats=PTS&playerstats=PTS" % (season, format, game_id)
        print score_url
        r = requests.get(score_url, auth=(SPORTS_FEED_USER, SPORTS_FEED_PSWD))
        score = json.loads(r.text)

        if not score:
            return None

        scores = score['gameboxscore']['quarterSummary']['quarterTotals']
        score_data = {'home_team': home_team, 'home_score': scores['homeScore'], 'away_team': away_team, 'away_score': scores['awayScore']}
        print score_data

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