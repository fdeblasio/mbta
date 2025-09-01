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

def writeToFile(file, text):
    file.write(text + "\n")

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

### Vehicles
api = "vehicles"
vehicleData = getData(api)
localBuses = ["132"]

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

#Merge attributes and relationships and move one level out
#Use current_status with stop

with open(api + ".txt", "w+") as vehicles:
    vehicles.seek(0)
    for vehicle in vehicleData:
        routeId = vehicle["relationships"]["route"]["data"]["id"]

        isBus = routeId[0].isdigit() and routeId not in localBuses
        isCR = routeId.startswith("CR")
        isShuttleGeneric = routeId.startswith("Shuttle-Generic")

        if not isBus and not isCR and not isShuttleGeneric:
            if routeId == "Red" or routeId.startswith("Green"):
                writeToFile(vehicles, routeId + " " + redGreenLine[vehicle["attributes"]["label"][:2]] + " " + vehicle["id"])
            else:
                writeToFile(vehicles, routeId + " " + vehicle["id"])
            for field in vehicle:
                if field == "attributes":
                    writeToFile(vehicles, "  " + field + ":")
                    for attribute in vehicle[field]:
                        attributeValue = vehicle[field][attribute]
                        if attribute == "carriages":
                            writeToFile(vehicles, "    " + attribute + ":")
                            for carriage in attributeValue:
                                writeToFile(vehicles, "      " + str(carriage))
                        elif attribute == "direction_id":
                            direction = "South" if attributeValue == 0 else "North"
                            writeToFile(vehicles, "    " + attribute + ": " + str(attributeValue) + " (" + direction + ")")
                        elif attribute != "revenue":
                            writeToFile(vehicles, "    " + attribute + ": " + str(attributeValue))
                elif field == "relationships":
                #if field == "relationships":
                    writeToFile(vehicles, "  " + field + ":")
                    for relationship in vehicle[field]:
                        if vehicle[field][relationship]["data"] is not None:
                            relationshipValue = vehicle[field][relationship]["data"]["id"]
                        else:
                            relationshipValue = "N/A"

                        if relationship == "stop":
                            writeToFile(vehicles, f"    {relationship}: {stopIdToName[relationshipValue]} ({relationshipValue})")
                        elif relationship == "trip":
                            writeToFile(vehicles, f"    {relationship}: {relationshipValue}")
                #elif field not in ["type", "links", "id"]:
                #    writeToFile(vehicles, "  " + field + ": " + str(vehicle[field]))
