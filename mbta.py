import json
import requests

def getData(api, getJson=False):
    if getJson:
        with open(api + ".json", "w+") as stops:
            stops.seek(0)
            stops.write(requests.get("https://api-v3.mbta.com/" + api).text)

    data = ""

    with open(api + ".json", "r+") as f:
        data = json.load(f)

    return data["data"]

### Stops
stopData = getData("stops")
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
lineData = getData("lines")
#
#with open(api + ".txt", "w+") as lines:
#    lines.seek(0)
#    for line in data:
#        lines.write(line["attributes"]["long_name"] + "\n")
#        for field in line:
#            if field != "type":
#                lines.write("  " + field + ": " + str(line[field]) + "\n")

### Vehicles
vehicleData = getData("vehicles")
