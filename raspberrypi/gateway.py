#!/usr/bin/env python3
# This Script functions as a basic gatway it checks for input from a RFID reader and then change the status of the object that is linked to the recieved uid
# A function that takes a uid from an RFID Chip (INT) and maps it to an URL (String)
import json
# This function generates a URL for a server request from an uid
def mapToUrl( uid ):
    url = 'http://server.localhost/#' + str(uid)
    return url
# This function searches a local json file for a specific uid | returns None if nothing is found else it returns a json object
def lookUpClothing( uid ):
    result = None
    data_file = open('clothing.json')
    data = json.load(data_file)
    for clothing in data["clothes_available"]:
        if uid == int(clothing["id"]):
            result = clothing
    return result
print(lookUpClothing(1234))
