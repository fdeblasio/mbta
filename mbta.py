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
api = "stops"
stopData = getData(api)
#
#with open(api + ".txt", "w+") as stops:
#    stops.seek(0)
#    for stop in stopData:
#        if stop["attributes"]["vehicle_type"] != 3:
#            stops.write(stop["attributes"]["name"] + "\n")
#            for field in stop:
#                if field != "type":
#                    stops.write("  " + field + ": " + str(stop[field]) + "\n")

### Lines
api = "lines"
lineData = getData(api)
#
#with open(api + ".txt", "w+") as lines:
#    lines.seek(0)
#    for line in lineData:
#        lines.write(line["attributes"]["long_name"] + "\n")
#        for field in line:
#            if field != "type":
#                lines.write("  " + field + ": " + str(line[field]) + "\n")

### Vehicles
api = "vehicles"
vehicleData = getData(api)
localBuses = ["132"]

with open(api + ".txt", "w+") as vehicles:
    vehicles.seek(0)
    for vehicle in vehicleData:
        routeId = vehicle["relationships"]["route"]["data"]["id"]
        if not routeId[0].isdigit() or routeId in localBuses:
            vehicles.write(routeId + " " + vehicle["id"] + "\n")
            for field in vehicle:
                if field == "attributes" or field == "relationships":
                    vehicles.write("  " + field + ":\n")
                    for value in vehicle[field]:
                        vehicles.write("    " + value + ": " + str(vehicle[field][value]) + "\n")
                elif field != "type":
                    vehicles.write("  " + field + ": " + str(vehicle[field]) + "\n")
