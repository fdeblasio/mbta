import json
import requests

def getData(api, getJson=False):
    if getJson:
        with open(api + ".json", "w+") as stops:
            stops.seek(0)
            request = "https://api-v3.mbta.com/" + api
            if api == "trips":
                request += "?filter%5Brevenue%5D=NON_REVENUE%2CREVENUE"
            stops.write(requests.get(request).text)

    data = ""
    with open(api + ".json", "r+") as f:
        data = json.load(f)
    return data["data"]

def writeToFile(file, text):
    file.write(text + "\n")

#replace with route lookup
def getDirection(direction_id):
    if direction_id == 0:
        return "Southbound"
    elif direction_id == 1:
        return "Northbound"

localBuses = ["132"]

### Stops
api = "stops"
stopData = getData(api)

stopIdToName = {"N/A" : "N/A"}

with open(api + ".txt", "w+") as stops:
    stops.seek(0)
    for stop in stopData:
        stopName = stop["attributes"]["name"]
        stopIdToName[stop["id"]] = stopName

        if stop["attributes"]["vehicle_type"] != 3:
            writeToFile(stops, stopName)
            for field in stop:
                if field != "type":
                    writeToFile(stops, "  " + field + ": " + str(stop[field]))

### Lines
#api = "lines"
#lineData = getData(api)
#
#with open(api + ".txt", "w+") as lines:
#    lines.seek(0)
#    for line in lineData:
#        writeToFile(lines, line["attributes"]["long_name"])
#        for field in line:
#            if field != "type":
#                writeToFile(lines, "  " + field + ": " + str(line[field]))

### Trips
#api = "trips"
#tripData = getData(api)
#
#with open(api + ".txt", "w+") as trips:
#    trips.seek(0)
#    for trip in tripData:
#        routeId = trip["relationships"]["route"]["data"]["id"]
#
#        isBus = routeId[0].isdigit() and routeId not in localBuses
#        isCR = routeId.startswith("CR")
#        #isShuttleGeneric = routeId.startswith("Shuttle-Generic")
#
#        #if not isBus and not isCR and not isShuttleGeneric:
#        if not isBus and not isCR:
#            writeToFile(trips, routeId + " " + trip["id"] + ":")
#            #writeToFile(trips, trip["attributes"]["long_name"])
#            for field in trip:
#                if field == "attributes":
#                    writeToFile(trips, "  " + field + ":")
#                    for attribute in trip[field]:
#                        attributeValue = trip[field][attribute]
#                        if attribute == "direction_id":
#                            writeToFile(trips, f"    {attribute}: {getDirection(attributeValue)} ({attributeValue})")
#                        elif attribute not in ["revenue", "wheelchair_accessible"] and attributeValue != "":
#                            writeToFile(trips, f"    {attribute}: {attributeValue}")
#                elif field == "relationships":
#                    writeToFile(trips, "  " + field + ":")
#                    for subfield in trip[field]:
#                        if subfield not in ["route", "shape"]:
#                            if trip[field][subfield]["data"] is not None:
#                                subfieldValue = trip[field][subfield]["data"]["id"]
#                            else:
#                                subfieldValue = "N/A"
#                            writeToFile(trips, f"    {subfield}: {subfieldValue}")

### Vehicles
api = "vehicles"
vehicleData = getData(api)

redGreenLine = {
    "15": "Pullman-Standard",
    "16": "Pullman-Standard",
    "17": "UTDC",
    "18": "Bombardier",
    "19": "CRRC",
    "20": "CRRC",
    "21": "CRRC",
    "35": "US Standard Light Rail Vehicle",
    "36": "Type 7",
    "37": "Type 7",
    "38": "Type 8",
    "39": "Type 9"
}

#Merge attributes and relationships and move one level out?
#Use current_status with stop?

#route lookup for direction - attributes/direction_names
with open(api + ".txt", "w+") as vehicles:
    vehicles.seek(0)
    for vehicle in vehicleData:
        routeId = vehicle["relationships"]["route"]["data"]["id"]

        isBus = routeId[0].isdigit() and routeId not in localBuses
        isCR = routeId.startswith("CR")
        isShuttleGeneric = routeId.startswith("Shuttle-Generic")

        if not isBus and not isCR and not isShuttleGeneric and vehicle["attributes"]["revenue"] == "REVENUE":
            if routeId == "Red" or routeId.startswith("Green"):
                writeToFile(vehicles, routeId + " " + redGreenLine[vehicle["attributes"]["label"][:2]] + " " + vehicle["id"])
            else:
                writeToFile(vehicles, routeId + " " + vehicle["id"])
            for field in vehicle:
                if field == "attributes":
                    writeToFile(vehicles, "  " + field + ":")
                    for attribute in vehicle[field]:
                        attributeValue = vehicle[field][attribute]
                        prefix = f"    {attribute}:"

                        if attribute == "carriages":
                            writeToFile(vehicles, prefix)
                            for carriage in attributeValue:
                                writeToFile(vehicles, f"      {carriage}")
                        elif attribute == "direction_id":
                            writeToFile(vehicles, f"{prefix} {getDirection(attributeValue)} ({attributeValue})")
                        elif attribute == "speed":
                            if attributeValue is None:
                                attributeValue = 0
                            writeToFile(vehicles, f"{prefix} {'%.2f'%(attributeValue*2.23694)} MPH ({attributeValue} mps)")
                        elif attribute != "revenue" and attributeValue is not None:
                            writeToFile(vehicles, f"{prefix} {attributeValue}")
                elif field == "relationships":
                #if field == "relationships":
                    writeToFile(vehicles, "  " + field + ":")
                    for relationship in vehicle[field]:
                        prefix = f"    {relationship}: "

                        if vehicle[field][relationship]["data"] is not None:
                            relationshipValue = vehicle[field][relationship]["data"]["id"]
                        else:
                            relationshipValue = "N/A"

                        if relationship == "stop":
                            writeToFile(vehicles, f"{prefix}{stopIdToName[relationshipValue]} ({relationshipValue})")
                        elif relationship == "trip":
                            writeToFile(vehicles, f"{prefix}{relationshipValue}")
                #elif field not in ["type", "links", "id"]:
                #    writeToFile(vehicles, "  " + field + ": " + str(vehicle[field]))
