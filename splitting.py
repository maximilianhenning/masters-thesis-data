import pandas as pd
import ast
import datetime
from os import path
import re

dir = path.dirname(__file__)
df_voyages_combined = pd.read_csv(path.join(dir, "combined/voyages.csv"), sep = ";")
df_people_combined = pd.read_csv(path.join(dir, "combined/people.csv"), sep = ";")

# Ships table
# ship_id   tons    guns    crew    type    built_by    built_year  built_at    owner       info
# ship_id   string  string  string  string  employee_id int         string      employee_id string

df_ships = df_voyages_combined[["ship_id", "name", "info"]]

def feature_getter(info, feature, min, max):
    result = info.split(feature)[0].strip().split(" ")[-1].strip("[\'")
    if "/" in result:
        result = result.split("/")
    if type(result) == list:
        min = result[0]
        max = result[1]
        result = int((int(min) + int(max)) / 2)
    return result, min, max

def ship_splitter(info):
    if type(info) == list:
        info = " ".join(info)
    tons = "nan"
    tons_min = "nan"
    tons_max = "nan"
    guns = "nan"
    guns_min = "nan"
    guns_max = "nan"
    crew = "nan"
    crew_min = "nan"
    crew_max = "nan"
    ship_type = "nan"
    built_by = "nan"
    built_year = "nan"
    built_at = "nan"
    # Tons, guns, crew and ship type work the same way
    if "tons" in info:
        tons, tons_min, tons_max = feature_getter(info, "tons", tons_min, tons_max)
    if "guns" in info:
        guns, guns_min, guns_max = feature_getter(info, "guns", guns_min, guns_max)
    if "crew" in info:
        crew, crew_min, crew_max = feature_getter(info, "crew", crew_min, crew_max)
    if "ship" in info:
        ship_type = info.split("ship")[0].strip().split(" ")[-1].strip("[\'").strip("\"")
    # Built by
    if "uilt by" in info:
        built_by = info.split("uilt by")[1].strip().split(" ")[0].strip(",")
        if "/" in built_by:
            built_by = built_by.split("/")
        if " at " in info:
            built_at_guess = info.split(" at ")[1].split(" ")[0].strip(",")
            # Don't take digits because tons can also be written like that
            if not built_at_guess.isdigit():
                built_at = built_at_guess
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
    return pd.Series([tons, tons_min, tons_max, guns, guns_min, guns_max, crew, crew_min, crew_max, ship_type, built_by, built_year, built_at])
df_ships_expand = df_ships["info"].apply(ship_splitter)
df_ships_expand.rename(columns = {0: "tons", 
                                  1: "tons_min", 
                                  2: "tons_max", 
                                  3: "guns", 
                                  4: "guns_min", 
                                  5: "guns_max", 
                                  6: "crew", 
                                  7: "crew_min", 
                                  8: "crew_max", 
                                  9: "type", 
                                  10: "built_by", 
                                  11: "built_year", 
                                  12: "built_at"}, inplace = True)
df_ships = pd.concat([df_ships, df_ships_expand], axis = 1)
df_ships.to_csv(path.join(dir, "output/ships.csv"), index = False, sep = ";")

# Voyages table
# voyage_id     ship    start   end     destination reference   captain
# voyage_id     ship_id string  string  place_id    string      employee_id

df_voyages_list = df_voyages_combined
df_voyages_list.drop(["name", "info"], axis = 1, inplace = True)
voyages_list = []
for row in df_voyages_list.iterrows():
    for x in range(1, 10):
        voyage_id = "voyage_" + str(x)
        # Check if cell is not nan (notna doesn't work on strings)
        if type(row[1][voyage_id]) == str:
            voyages_list.append([row[1]["ship_id"], x, row[1][voyage_id]])
df_voyages = pd.DataFrame(voyages_list)
df_voyages.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "raw"}, inplace = True)
def voyage_id_creator(row):
    voyage_id = row["ship_id"] + "v" + str(row["voyage_id"])
    return voyage_id
df_voyages["voyage_id"] = df_voyages.apply(voyage_id_creator, axis = 1)

def voyage_splitter(raw):
    start = "nan"
    end = "nan"
    destination = "nan"
    captain = "nan"
    reference_string = "nan"
    if str(raw) != "nan":
        raw = ast.literal_eval(raw)
        # Start & End
        if type(raw["time"]) == list:
            start = raw["time"][0]
            end = raw["time"][1]
        else:
            start = raw["time"]
            end = raw["time"]
        # Destination
        destination = raw["destination"]
        if not destination:
            destination = "nan"
        # Reference
        references = raw["reference"]
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
        captain = raw["captain"]
        if type(captain) == list:
            captain = "nan"
    return pd.Series([start, end, destination, captain, reference_string])
    #return captain
df_voyages_expand = df_voyages["raw"].apply(voyage_splitter)
df_voyages_expand.rename(columns = {0: "start", 1: "end", 2: "destination", 3: "captain", 4: "references"}, inplace = True)
df_voyages = pd.concat([df_voyages, df_voyages_expand], axis = 1)
df_voyages.to_csv(path.join(dir, "output/voyages.csv"), index = False, sep = ";")

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
    raw = row[1]["raw"]
    if str(raw) != "nan":
        raw = ast.literal_eval(raw)
        # If there is an itinerary, read it
        if "itinerary" in raw.keys():
            itinerary = raw["itinerary"]
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
                if len(location) > 2:
                    special = True
                if location:
                    location = " ".join(location)
                else:
                    location = "nan"
                call_list.append([ship_id, voyage_id, call_id, call, year, month, day, location, special])
df_calls = pd.DataFrame(call_list)
df_calls.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "call_id", 3: "raw", 4: "year", 5: "month", 6: "day", 7: "location", 8: "special"}, inplace = True)
def call_id_creator(row):
    call_id = row["voyage_id"] + "c" + str(row["call_id"])
    return call_id
df_calls["call_id"] = df_calls.apply(call_id_creator, axis = 1)
df_calls.to_csv(path.join(dir, "output/calls.csv"), index = False, sep = ";")

# Location table
# location_id   longitude   latitude
# location_id   float       float

location_list = []
location_list += df_calls.loc[df_calls["special"] == False]["location"].tolist()
location_list += df_ships.loc[df_ships["built_at"].notna()]["built_at"].tolist()
location_list = list(set(location_list))

# People table
# person_id     last_name   first_name  birth_date  death_date  birth_location  baptised_location   mother_name father_name
# person_id     string      string      string      string      location_id     location_id         string      string      

def person_line_expander(person):
    last_name = "nan"
    first_name = "nan"
    birth_date = "nan"
    death_date = "nan"
    person_split = person.split(",")
    last_name = person_split[0].strip()
    if len(person_split) > 1:
        first_name = re.compile("[^a-zA-Z\s]").sub("", person_split[1]).strip()
        if "-" in person:
            dates = re.compile("[a-zA-Z,\(\)]").sub("", person_split[1]).strip()
            if dates:
                if dates[0] == "-":
                    death_date = dates.strip("-")
                elif dates[-1] == "-":
                    birth_date = dates.strip("-")
                elif len(dates) > 4:
                    birth_date = dates.split("-")[0]
                    death_date = dates.split("-")[1]
    result_series = pd.Series([last_name, first_name, birth_date, death_date])
    return result_series

def person_info_expander(info):
    birth_location = "nan"
    baptised_location = "nan"
    mother_name = "nan"
    father_name = "nan"
    # XXXX baptised_location
    if ";" in str(info):
        info_tokens = info.split(";")
    else: 
        info_tokens = [info]
    for token in info_tokens:
        token = str(token)
        if "b " in token and not " bap " in token:
            birth_location = token.strip("b ")
            if "s of" in birth_location:
                birth_location = birth_location.split("s of")[0]
            birth_location = birth_location.split(" ")
            birth_tokens = []
            for token in birth_location:
                if not token == "in" and not token.isdigit() and not token in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                    birth_tokens.append(token)
            birth_location = " ".join(birth_tokens).strip()
        if " s of " in token:
            print(token)
            parents = token.split(" s of ")[1]
            parents_split = parents.split("&")
            if len(parents_split) > 1:
                father_name = parents_split[0].strip()
                mother_name = parents_split[1].strip()
            if "bap" in token:
                baptised_location = token.split("bap")[1].split(", s of")[0]
                baptised_location = baptised_location.split(" ")
                baptised_tokens = []
                for token in baptised_location:
                    if not token.isdigit() and not token in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                        baptised_tokens.append(token)
                baptised_location = " ".join(baptised_tokens).strip()
    return pd.Series([birth_location, baptised_location, mother_name, father_name])

df_people = df_people_combined
df_people[["last_name", "first_name", "birth_date", "death_date"]] = df_people["person"].apply(person_line_expander)
df_people[["birth_location", "baptised_location", "mother_name", "father_name"]] = df_people["info"].apply(person_info_expander)
df_people.to_csv(path.join(dir, "output/people.csv"), index = False, sep = ";")

# Jobs table
# person_id     job_id      job     ship_id     voyage_id
# person_id     job_id      string  ship_id     voyage_id

# Fill in IDs for relevant features in all tables
# XXXX