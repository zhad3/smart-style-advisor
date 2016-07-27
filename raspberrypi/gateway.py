#!/usr/bin/env python3
# This Script functions as a basic gatway it checks for input from a RFID reader and then change the status of the object that is linked to the recieved uid

import json
import requests
import serial

# A function that takes a uid from an RFID Chip (HEXADECIMAL) and maps it to an URL (String) or returns None if the uid is not formatted correctly
def mapToUrl( uid ):
    # The first 2 hexadecimal characters (00-ff) need to be present (manufacturer id) aswell as a following id (clothing id)
    if len(uid) > 2:
        baseurl = 'http://server.localhost/'
        manid = int(uid[:2],16)
        clothid = uid[2:] # Do not convert to int
        return baseurl+'?mid='+str(manid)+'&cid='+str(clothid)
    else:
        return None

# This function returns a json Object from a specified file
def getJsonFromFile( fileName ):
    data_file = open(fileName)
    data = json.load(data_file)
    return data

# This function searches a local json file for a specific uid | returns None if nothing is found else it returns a json object
def lookUpClothing( uid ):
    result = None
    data = getJsonFromFile('clothing.json')
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
            is_available = 0
            info[0]["is_available"] = 0
            print('Clothing ' + clothing['name'] + ' is now unavailable')
        # Case 1.2 : Clothing was not in the closet and was just inserted
        else:
            is_available = 1
            info[0]["is_available"] = 1
            print('Clothing ' + clothing['name'] + ' is now available')

        print("is_available:",is_available)
        print("info[1]:",info[1])
        print("info[0][\"is_available\"]:",info[0]["is_available"])
        print("data[0][\"is_available\"]:",data[0]["is_available"])
        json.dump(data, open('clothing.json', 'w'))
    # Case 2 : clothing is not in DB and has to be retrieved from server
    #else:
        #url = "http://localhost:3000" # Dummy URL for testing environment -> mapToUrl
        #r = requests.get(url)
        #info = r.json()
        #data = getJsonFromFile('clothing.json')
        #data["clothes_available"].append(info)
        #json.dump(data, open('clothing.json', 'w'))
        #print('ID was not in local database -- found on server -- added to local db')
        #print('Clothing ' + info['name'] + ' is now available!')
    return

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

