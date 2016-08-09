#!/usr/bin/env python3

import json
import requests
import time
from bottle import route, run, response

@route('/weather')
def weather():
	now = int(time.time())
	lastqueried = getJsonFromFile('time.json')
        if lastqueried != None:
	    last = int(lastqueried['time'])
        else:
            last = now - 600
	difference = now - last
	if difference > 600:
		print('current weather data is older than 10 minutes -- fetching from server')
		getOnlineWeatherData(2934691)
		f = open('time.json', 'w')
		try:
			json.dump({"time": str(now)}, f)
		finally:
			f.close()
	# Now return actual weather data
	weatherData = getLocalWeatherData()
	return weatherData

# This function returns a json Object from a specified file
def getJsonFromFile( fileName ):
    try:
        data_file = open(fileName)
    except IOError:
        data_file = open(fileName,"w+")
    try:
        data = json.load(data_file)
    except ValueError:
        print("Could not parse"+fileName)
        return None
    return data

def getOnlineWeatherData( cityID ): #Duisburg 2934691
	url = "http://api.openweathermap.org/data/2.5/weather?id=" + str(cityID) +"&APPID=154e9a2853bb39627c17906e69f7a56c&units=metric"
        try:
	    r = requests.get(url)
	    weather = r.json()
        except:
            print("Could not retrieve weather data from server. Trying local data.")
            return
	f = open('weather.json', 'w')
	try:
		json.dump(weather, f)
	finally:
		f.close
def getLocalWeatherData():
	data = getJsonFromFile('weather.json')
	return data

@route('/clothing/<manid>/<clothid>')
def getClothingData(manid,clothid):
	# Concatenate manid and clothid
	manid = hex(int(manid))[2:] # Remove the preceeding '0x'
	id = str(manid)+str(clothid)
	data = getJsonFromFile('serverClothing.json')
	for clothing in data:
		if clothing["id"] == id:
			response.content_type = 'application/json'
			return clothing

run(host='localhost', port=3333, debug=True)
