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
#stopData = getData(api)
#
#with open(api + ".txt", "w+") as stops:
#    stops.seek(0)
#    for stop in stopData:
#        if stop["attributes"]["vehicle_type"] != 3:
#            writeToFile(stops, stop["attributes"]["name"])
#            for field in stop:
#                if field != "type":
#                    writeToFile(stops, "  " + field + ": " + str(stop[field]))

### Lines
api = "lines"
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

greenLine = {
    36: "Type 7",
    37: "Type 7",
    38: "Type 8",
    39: "Type 9"
}

redLine = {
    15: "Pullman-Standard",
    16: "Pullman-Standard",
    17: "UTDC",
    18: "Bombardier",
    19: "CRRC",
    20: "CRRC",
    21: "CRRC"
}

with open(api + ".txt", "w+") as vehicles:
    vehicles.seek(0)
    for vehicle in vehicleData:
        routeId = vehicle["relationships"]["route"]["data"]["id"]

        isBus = routeId[0].isdigit() and routeId not in localBuses
        isCR = routeId.startswith("CR")

        if not isBus and not isCR:
            writeToFile(vehicles, routeId + " " + vehicle["id"])
            for field in vehicle:
                if field == "attributes" or field == "relationships":
                    vehicles.write("  " + field + ":\n")
                    for value in vehicle[field]:
                        if value == "carriages":
                            writeToFile(vehicles, "    " + value + ":")
                            for carriage in vehicle[field][value]:
                                writeToFile(vehicles, "      " + str(carriage))
                        elif value != "revenue":
                            writeToFile(vehicles, "    " + value + ": " + str(vehicle[field][value]))
                elif field not in ["type", "links", "id"]:
                    writeToFile(vehicles, "  " + field + ": " + str(vehicle[field]))
