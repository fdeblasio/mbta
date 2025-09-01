import json
import requests

def getJson(api):
    with open(api + ".json", "w+") as stops:
        stops.seek(0)
        stops.write(requests.get("https://api-v3.mbta.com/" + api).text)

### Stops

##with open("stops.json", "w+") as stops:
##    stops.seek(0)
##    stops.write(requests.get("https://api-v3.mbta.com/stops").text)
#
#data = ""
#
#with open("stops.json", "r+") as f:
#    data = json.load(f)
#
#data = data["data"]
#
#with open("stops.txt", "w+") as stops:
#    stops.seek(0)
#    for stop in data:
#        if stop["attributes"]["vehicle_type"] != 3:
#            stops.write(stop["attributes"]["name"] + "\n")
#            for field in stop:
#                if field != "type":
#                    stops.write("  " + field + ": " + str(stop[field]) + "\n")
### Lines

#api = "lines"
##with open(api + ".json", "w+") as stops:
##    stops.seek(0)
##    stops.write(requests.get("https://api-v3.mbta.com/" + api).text)
#
#data = ""
#
#with open(api + ".json", "r+") as f:
#    data = json.load(f)
#
#data = data["data"]
#
#with open(api + ".txt", "w+") as lines:
#    lines.seek(0)
#    for line in data:
#        lines.write(line["attributes"]["long_name"] + "\n")
#        for field in line:
#            if field != "type":
#                lines.write("  " + field + ": " + str(line[field]) + "\n")

### Vehicles
#getJson("vehicles")