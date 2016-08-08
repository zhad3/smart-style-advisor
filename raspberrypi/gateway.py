#!/usr/bin/env python3
# This Script functions as a basic gatway it checks for input from a RFID reader and then change the status of the object that is linked to the recieved uid

import json
import requests
import serial

# A function that takes a uid from an RFID Chip (HEXADECIMAL) and maps it to an URL (String) or returns None if the uid is not formatted correctly
def mapToUrl( uid ):
    # The first 2 hexadecimal characters (00-ff) need to be present (manufacturer id) aswell as a following id (clothing id)
    if len(uid) > 2:
        baseurl = 'http://localhost:3333/clothing/'
        manid = int(uid[:2],16)
        clothid = uid[2:] # Do not convert to int
        return baseurl+str(manid)+'/'+str(clothid)
    else:
        return None

# This function returns a json Object from a specified file
def getJsonFromFile( fileName ):
    data = None
    try:
        data_file = open(fileName)
    except IOError:
        data_file = open(fileName,"w+")
    try:
        data = json.load(data_file)
    except ValueError:
        return None
    return data

# This function searches a local json file for a specific uid | returns None if nothing is found else it returns a json object
def lookUpClothing( uid ):
    result = None
    data = getJsonFromFile('clothing.json')
    if data == None:
        return None
    for clothing in data:
        if uid == clothing["id"]:
            result = (clothing, clothing["is_available"], data)
    return result

# This function will be executed if an uid was successfully received
def processID( uid ):
    info = lookUpClothing(uid)
    # Case 1 : clothing is already stored in DB
    if info != None:
        print('found ID in local database')
        clothing = info[0]      # JSON Object
        is_available = info[1]  # Boolean
        data = info[2]          # JSON Object Array
        # Case 1.1 : Clothing was in the closet and was just removed
        if is_available:
            info[0]["is_available"] = 0
            print('Clothing ' + clothing['name'] + ' is now unavailable')
        # Case 1.2 : Clothing was not in the closet and was just inserted
        else:
            info[0]["is_available"] = 1
            print('Clothing ' + clothing['name'] + ' is now available')

        json.dump(data, open('clothing.json', 'w'))
    # Case 2 : clothing is not in DB and has to be retrieved from server
    else:
        url = mapToUrl(uid)
        if url != None:
            r = requests.get(url)
            data = []
            newinfo = {}
            try:
                newinfo = r.json()
            except ValueError:
                print("Couldn't retrieve clothing data from server",r.status_code,r.headers['content-type'],r.encoding,r.text)
                return

            newinfo["is_available"] = 1

            try:
                data = getJsonFromFile('clothing.json')
            except ValueError:
                data = []
            if data == None:
                data = []
            data.append(newinfo)
            json.dump(data, open('clothing.json', 'w'))
            print('ID was not in local database -- found on server -- added to local db')
            print('Clothing ' + newinfo['name'] + ' is now available!')

    # Send recommended clothing to display server
    rec_clothing,weather,temp = getRecClothList()
    post_data = {"clothing":rec_clothing,"weather":weather["weather"],"temp":temp}
    print("Trying to send data: ",post_data)
    try:
        r = requests.post('http://localhost:3000/updateClothing', json=post_data, timeout=0.5)
    except requests.exceptions.Timeout:
        print("Post request to display server timed out")

    return

# This function takes the current temperature and returns a list of clothing that fits the temperature
# Clothing types:
#     pants
#     top
#     shoes
def getRecClothList():
    rec_clothing = []
    found_clothing_types = []
    cloth_data = getJsonFromFile("clothing.json")
    if cloth_data == None:
        return rec_clothing

    # Get temperature
    temp = 10
    weather = None
    r = requests.get("http://localhost:3333/weather")
    try:
        weather = r.json()
    except ValueError,e:
        print("Couldn't get weather data",r.text,e.args)
        return rec_clothing

    temp = int(weather["main"]["temp"])

    for clothing in cloth_data:
        # Depending on the temperature we decide which clothing we wish to recommend
        if temp < 15:
            # Cold
            if clothing["subtype"] in ["jeans","sneakers","sweater"] and clothing["is_available"]:
                rec_clothing.append(clothing)
                if clothing["type"] not in found_clothing_types:
                    found_clothing_types.append(clothing["type"])
        elif temp > 15 and temp < 20:
            # Warm
            if clothing["subtype"] in ["jeans","sneakers","shirt"] and clothing["is_available"]:
                rec_clothing.append(clothing)
                if clothing["type"] not in found_clothing_types:
                    found_clothing_types.append(clothing["type"])
        elif temp > 20:
            # Hot
            if clothing["subtype"] in ["shorts","sneakers","shirt"] and clothing["is_available"]:
                rec_clothing.append(clothing)
                if clothing["type"] not in found_clothing_types:
                    found_clothing_types.append(clothing["type"])

    # There is atleast one type (pants, top or shoes) that we couldn't find any fitting clothing for
    # Try again with fallbacks adding clothing with no fitting subtype (wear jeans even though its hot)
    if len(found_clothing_types) < 3:
        for clothing in cloth_data:
            if clothing["type"] not in found_clothing_types and clothing["is_available"]:
                rec_clothing.append(clothing)

    return rec_clothing,weather,temp

# The device might change depending on how many other devices are connected to the raspberry pi
# or when using a different distribution/os
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
while 1:
    uid = ser.readline().rstrip('\r\n')
    if uid != "":
        url = mapToUrl(uid)
        if url != None:
            print(uid+" -> "+url)
            processID(uid)
        else:
            print(uid+" -> Bad url format")

