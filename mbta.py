import json
import requests
import sys

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
def getDirection(routeId, direction_id):
    return f"{routeIdAttributes[routeId]['direction_names'][direction_id].lower()} to {routeIdAttributes[routeId]['direction_destinations'][direction_id]}"

def valueToText(text):
    return text.capitalize().replace("_", " ")

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

### Routes
api = "routes"
routeData = getData(api)

routeIdAttributes = {}

with open(api + ".txt", "w+") as routes:
    routes.seek(0)
    for route in routeData:
        routeId = route["id"]
        routeIdAttributes[routeId] = route["attributes"]

        writeToFile(routes, routeId)
        for field in route:
            if field not in ["id", "links", "type"]:
                writeToFile(routes, "  " + field + ":")
                for subfield in route[field]:
                    value = route[field][subfield]
                    writeToFile(routes, f"    {subfield}: {value}")

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
#                            writeToFile(trips, f"    {attribute}: {getDirection(routeId, attributeValue)} ({attributeValue})")
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

updateJson = sys.argv[1] if len(sys.argv) > 1 else False

vehicleData = getData(api, updateJson)

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

vehicleDict = {}

for vehicle in vehicleData:
    routeId = vehicle["relationships"]["route"]["data"]["id"]

    isBus = routeId[0].isdigit() and routeId not in localBuses
    isCR = routeId.startswith("CR")
    isShuttleGeneric = routeId.startswith("Shuttle-Generic")

    attributes = vehicle["attributes"]
    stopData = vehicle["relationships"]["stop"]["data"]

    if not isBus and not isCR and not isShuttleGeneric and stopData is not None and attributes["revenue"] == "REVENUE":
        #SL and CT should use short_name but cross that bridge if it ever gets used
        #Unsure about CR
        vehicleId = vehicle["id"]
        vehicleTitle = f" - {vehicleId}"
        if routeId in localBuses:
            vehicleTitle = f"{routeId} ({routeIdAttributes[routeId]['long_name']})" + vehicleTitle
        else:
            vehicleTitle = routeIdAttributes[routeId]["long_name"] + vehicleTitle
            if routeId == "Red" or routeId.startswith("Green"):
                vehicleTitle += f" ({redGreenLine[vehicle['attributes']['label'][:2]]})"
        vehicleInfo = vehicleTitle + "\n"

        directionInfo = f"  Heading {getDirection(routeId, attributes['direction_id'])}"
        speed = attributes["speed"]
        if speed is not None:
            directionInfo += f" at {'%.2f'%(speed*2.23694)} MPH ({speed} mps)"
        vehicleInfo += directionInfo + "\n"

        vehicleInfo += f"  {valueToText(attributes['current_status'])} {stopIdToName[stopData['id']]}\n"
        vehicleInfo += f"  Located at {attributes['latitude']}, {attributes['longitude']} with bearing {attributes['bearing']}\n"

        carriages = "  Carriages:"
        for carriage in attributes["carriages"]:
            if carriage["occupancy_percentage"] is not None:
                carriages += (f"\n    {carriage['label']}: {valueToText(carriage['occupancy_status'])} ({carriage['occupancy_percentage']}% full)")
        if carriages != "  Carriages:":
            vehicleInfo += carriages + "\n"

        lastUpdated = attributes["updated_at"].split("T")
        lastDate = lastUpdated[0]
        lastTime = lastUpdated[1].split("-")[0]
        vehicleInfo += f"  Last updated at {lastTime} on {lastDate}\n"

        vehicleDict[f"{routeId} {vehicleId}"] = vehicleInfo

with open(api + ".txt", "w+") as vehicles:
    vehicles.seek(0)
    for vehicle in sorted(vehicleDict.values()):
        writeToFile(vehicles, vehicle)

with open(api + ".html", "w+") as vehiclesHTML:
    vehiclesHTML.seek(0)
    writeToFile(vehiclesHTML, "<html>")
    writeToFile(vehiclesHTML, "<head>")
    writeToFile(vehiclesHTML, "<style>")
    writeToFile(vehiclesHTML, "  body {font-family: 'Helvetica', sans-serif;}")
    writeToFile(vehiclesHTML, "</style>")
    writeToFile(vehiclesHTML, "</head>")
    writeToFile(vehiclesHTML, "<body>")
    for vehicle in sorted(vehicleDict):
        routeId = vehicle.split()[0]
        writeToFile(vehiclesHTML, f"<p style=\"color:#{routeIdAttributes[routeId]['text_color']};background-color:#{routeIdAttributes[routeId]['color']};\">")
        textLines = vehicleDict[vehicle].split("\n")
        header = textLines[0]
        header = header.replace("(CRRC)", "<b>(CRRC)</b>")
        header = header.replace("(Type 9)", "<b>(Type 9)</b>")
        writeToFile(vehiclesHTML, f"<span style='font-weight: bold'>{header}</span><br>")
        for textLine in textLines[1:]:
        #for textLine in textLines:
            if textLine != "":
                htmlLine = textLine.replace("  ", "&nbsp;&nbsp;")
                writeToFile(vehiclesHTML, htmlLine + "<br>")
        writeToFile(vehiclesHTML, "</p>")
    writeToFile(vehiclesHTML, "</body>")
    writeToFile(vehiclesHTML, "</html>")
