import pandas as pd
import ast
import datetime
from os import path

path = path.dirname(__file__)
df_combined = pd.read_csv(path + "/combined.csv", sep = ";")

# Ships table
# ship_id   tons    guns    crew    type    built_by    built_year  Owner   info
# ship_id   string  string  string  string  string      string      string  string

df_ships = df_combined[["ship_id", "name", "info"]]

def feature_getter(info, feature):
    feature_result = info.split(feature)[0].strip().split(" ")[-1].strip("[\'")
    if "/" in feature_result:
        feature_result = feature_result.split("/")
    return feature_result

def ship_splitter(info):
    if type(info) == list:
        info = " ".join(info)
    tons = "nan"
    guns = "nan"
    crew = "nan"
    ship_type = "nan"
    built_by = "nan"
    built_year = "nan"
    # Tons, guns, crew and ship type work the same way
    if "tons" in info:
        tons = feature_getter(info, "tons")
    if "guns" in info:
        guns = feature_getter(info, "guns")
    if "crew" in info:
        crew = feature_getter(info, "crew")
    if "ship" in info:
        ship_type = feature_getter(info, "ship")
    # Built by
    if "uilt by" in info:
        built_by = info.split("uilt by")[1].strip().split(" ")[0].strip(",")
        if "/" in built_by:
            built_by = built_by.split("/")
    # Built year can be written in two different ways
    for word in ["uilt", "aunched"]:
        if word in info:
            built_check = info.split(str(word))[1].strip()
            if built_check[0].isnumeric():
                built_year = built_check.split(" ")[0].strip(",")
    # Principal Managing Owner
    # XXXX
    # Technical measurements
    # XXXX
    return pd.Series([tons, guns, crew, ship_type, built_by, built_year])
df_ships_expand = df_ships["info"].apply(ship_splitter)
df_ships_expand.rename(columns = {0: "tons", 1: "guns", 2: "crew", 3: "type", 4: "built_by", 5: "built_year"}, inplace = True)
df_ships = pd.concat([df_ships, df_ships_expand], axis = 1)
df_ships.to_csv(path + "/Output/ships.csv", index = False, sep = ";")

# Voyages table
# voyage_id     ship    start   end     destination reference   captain
# voyage_id     ship_id string  string  place_id    string      employee_id

df_voyages_list = df_combined
df_voyages_list.drop(["name", "info"], axis = 1, inplace = True)
voyages_list = []
for row in df_voyages_list.iterrows():
    for x in range(1, 10):
        voyage_id = "voyage_" + str(x)
        # Check if cell is not nan (notna doesn't work on strings)
        if type(row[1][voyage_id]) == str:
            voyages_list.append([row[1]["ship_id"], x, row[1][voyage_id]])
df_voyages = pd.DataFrame(voyages_list)
df_voyages.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "info"}, inplace = True)
def id_creator(voyage_id):
    return "v" + str(voyage_id)
df_voyages["voyage_id"] = df_voyages["voyage_id"].apply(id_creator)

def voyage_splitter(info):
    start = "nan"
    end = "nan"
    destination = "nan"
    captain = "nan"
    reference_string = "nan"
    if str(info) != "nan":
        info = ast.literal_eval(info)
        # Start & End
        if type(info["time"]) == list:
            start = info["time"][0]
            end = info["time"][1]
        else:
            start = info["time"]
            end = info["time"]
        # Destination
        destination = info["destination"]
        if not destination:
            destination = "nan"
        # Reference
        references = info["reference"]
        if len(references) > 0:
            reference_string = ""
            for reference in references:
                reference = reference.strip()
                reference = "\"" + reference + "\""
                reference_string += reference
                if not len(references) == 1:
                    reference_string += ","
                references = references[1:]
        # Fill in start & end if they don't exist yet but stops do
        # Captain
        captain = info["captain"]
        if type(captain) == list:
            captain = "nan"
    return pd.Series([start, end, destination, captain, reference_string])
    #return captain
df_voyages_expand = df_voyages["info"].apply(voyage_splitter)
df_voyages_expand.rename(columns = {0: "start", 1: "end", 2: "destination", 3: "captain", 4: "references"}, inplace = True)
df_voyages = pd.concat([df_voyages, df_voyages_expand], axis = 1)
df_voyages.to_csv(path + "/Output/voyages.csv", index = False, sep = ";")

# Calls table
# ship_id   voyage_id   call_id     raw     year    month   day    place        special
# ship_id   voyage_id   call_id     string  int     int     int    place_id     boolean    

call_list = []
# Go through all voyages
for row in df_voyages.iterrows():
    # Get ship id and voyage id
    ship_id = row[1]["ship_id"]
    voyage_id = row[1]["voyage_id"]
    # Read info dictionary
    info = row[1]["info"]
    if str(info) != "nan":
        info = ast.literal_eval(info)
        # If there is an itinerary, read it
        if "itinerary" in info.keys():
            itinerary = info["itinerary"]
            calls = itinerary.split("-")
            # Go through calls
            call_id = 0
            for call in calls:
                call_id += 1
                call = call.strip()
                call_parts = call.split(" ")
                month = "nan"
                day = "nan"
                location = []
                special = False
                # Classify parts
                for part in call_parts:
                    # Get digits
                    if part.isdigit():
                        if len(part) == 4:
                            year = part
                        else:
                            day = part
                    # Get other characters
                    else:
                        # Convert month abbreviation to number
                        if part in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                            month = datetime.datetime.strptime(part, "%b").month
                        # Add all others to location
                        else:
                            location.append(part)
                # If there is so much written, it must be special somehow
                if len(location) > 3:
                    special = True
                if location:
                    location = " ".join(location)
                else:
                    location = "nan"
                call_list.append([ship_id, voyage_id, call_id, call, year, month, day, location, special])
df_calls = pd.DataFrame(call_list)
df_calls.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "call_id", 3: "raw", 4: "year", 5: "month", 6: "day", 7: "location", 8: "special"}, inplace = True)
df_calls.to_csv(path + "/Output/calls.csv", index = False, sep = ";")
def id_creator(calls_id):
    return "c" + str(calls_id)
df_calls["call_id"] = df_calls["call_id"].apply(id_creator)
print(df_calls.head())

# Location table
# location_id   longitude   latitude
# location_id   float       float

# Employee table
# employee_id   owned   captained
# employee_id   ship_id voyage_id

# Fill in IDs for relevant features in all tables
# XXXX