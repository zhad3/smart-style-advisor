#!/usr/bin/env python3

import json
import requests
from bottle import route, run

@route('/weather')
def weather():
	return str(time)#getJsonFromFile('weather.json')

# This function returns a json Object from a specified file
def getJsonFromFile( fileName ):
    data_file = open(fileName)
    data = json.load(data_file)
    return data

def getOnlineWeatherData( cityID ):
	url = "http://api.openweathermap.org/data/2.5/weather?id=" + str(cityID) +"2860410&APPID=154e9a2853bb39627c17906e69f7a56c&units=metric"
	r = requests.get(url)
	weather = r.json()
	json.dump(data, open('weather.json', 'w'))

run(host='localhost', port=3000, debug=True)