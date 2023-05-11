import pandas as pd
import ast
import datetime
from os import path
import re
from unidecode import unidecode

dir = path.dirname(__file__)
voyages_combined_df = pd.read_csv(path.join(dir, "combined/voyages.csv"), sep = ";")
people_df_combined = pd.read_csv(path.join(dir, "combined/people.csv"), sep = ";")

# Ships table
# ship_id   tons    tons_min    tons_max    guns    guns_min    guns_max    crew    crew_min    crew_max
# ship_id   int     int         int         int     int         int         int     int         int
# 
# type    built_by    built_year  built_at        owner       info
# string  person_id   int         location_id     person_id   string

ships_df = voyages_combined_df[["ship_id", "name", "info"]]

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
ships_expand_df = ships_df["info"].apply(ship_splitter)
ships_expand_df.rename(columns = {0: "tons", 
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
ships_df = pd.concat([ships_df, ships_expand_df], axis = 1)
print("Ships done")

# Voyages table
# voyage_id     ship    start   end     destination reference   captain
# voyage_id     ship_id string  string  place_id    string      employee_id

voyages_df_list = voyages_combined_df
voyages_df_list.drop(["name", "info"], axis = 1, inplace = True)
voyages_list = []
for row in voyages_df_list.iterrows():
    for x in range(1, 10):
        voyage_id = "voyage_" + str(x)
        # Check if cell is not nan (notna doesn't work on strings)
        if type(row[1][voyage_id]) == str:
            voyages_list.append([row[1]["ship_id"], x, row[1][voyage_id]])
voyages_df = pd.DataFrame(voyages_list)
voyages_df.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "raw"}, inplace = True)
def voyage_id_creator(row):
    voyage_id = row["ship_id"] + "v" + str(row["voyage_id"])
    return voyage_id
voyages_df["voyage_id"] = voyages_df.apply(voyage_id_creator, axis = 1)

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
voyages_df_expand = voyages_df["raw"].apply(voyage_splitter)
voyages_df_expand.rename(columns = {0: "start", 1: "end", 2: "destination", 3: "captain", 4: "references"}, inplace = True)
voyages_df = pd.concat([voyages_df, voyages_df_expand], axis = 1)
print("Voyages done")

# Calls table
# ship_id   voyage_id   call_id     raw     year    month   day    location     special
# ship_id   voyage_id   call_id     string  int     int     int    location_id  boolean    

call_list = []
# Go through all voyages
for row in voyages_df.iterrows():
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
                # If there is no capital letter, it could be special
                special = True
                for location_part in location:
                    for char in location_part:
                        if char.isupper():
                            special = False
                # If they write so much about it, it must be special somehow
                if len(location) > 2 and location not in ["East India Dock", "Fort St David", "St Augustine's Bay", "Rio de Janeiro"]:
                    special = True
                if location:
                    location = " ".join(location)
                    location = location.strip("'")
                else:
                    location = "nan"
                call_list.append([ship_id, voyage_id, call_id, call, year, month, day, location, special])
calls_df = pd.DataFrame(call_list)
calls_df.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "call_id", 3: "raw", 4: "year", 5: "month", 6: "day", 7: "location", 8: "special"}, inplace = True)
def call_id_creator(row):
    call_id = row["voyage_id"] + "c" + str(row["call_id"])
    return call_id
calls_df["call_id"] = calls_df.apply(call_id_creator, axis = 1)
print("Calls done")

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
    baptised_parish = "nan"
    baptised_city = "nan"
    mother_name = "nan"
    mother_origin = "nan"
    father_name = "nan"
    father_job = "nan"
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
            if "," in birth_location:
                birth_location = birth_location.split(",")[0].strip()
        if " s of " in token:
            parents = token.split(" s of ")[1]
            parents_split = parents.split("&")
            if len(parents_split) > 1:
                father = parents_split[0]
                if "," in father:
                    father_split = father.split(",")
                    if len(father_split) > 1:
                        father_name = father_split[0].strip()
                        father_job = father_split[1].strip()
                else:
                    father_name = father.strip()
                mother = parents_split[1]
                if ", of" in mother:
                    mother_split = mother.split(", of")
                    if len(mother_split) > 1:
                        mother_name = mother_split[0].strip()
                        mother_origin = mother_split[1].strip()
                else:
                    mother_name = mother.strip()
            if "bap" in token:
                baptised_location = token.split("bap")[1].split(", s of")[0]
                baptised_location = baptised_location.split(" ")
                baptised_tokens = []
                for token in baptised_location:
                    if not token.isdigit() and not token in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                        baptised_tokens.append(token)
                baptised_location = " ".join(baptised_tokens).strip()
                if "," in baptised_location:
                    baptised_parish = baptised_location.split(", ")[0].strip()
                    baptised_city = baptised_location.split(", ")[1].strip()
                else:
                    baptised_city = baptised_location
    return pd.Series([birth_location, baptised_parish, baptised_city, mother_name, mother_origin, father_name, father_job])

people_df = people_df_combined
people_df[["last_name", "first_name", "birth_date", "death_date"]] = people_df["person"].apply(person_line_expander)
people_df[["birth_location", "baptised_parish", "baptised_city", "mother_name", "mother_origin", "father_name", "father_job"]] = people_df["info"].apply(person_info_expander)
print("People done")

# Jobs table
# person_id     job_id      job         voyage_id
# person_id     job_id      string      voyage_id

# XXXX Add run etc
# XXXX Add (principal managing) owner

def job_token_reader(token, job_counter):
    voyage_ship = "nan"
    voyage_start = "nan"
    voyage_end = "nan"
    voyage = re.sub(job, "", token, flags = re.IGNORECASE).strip()
    voyage_split = voyage.split(" ")
    voyage_ship = " ".join([token for token in voyage_split if not "/" in token])
    voyage_dates = " ".join([token for token in voyage_split if "/" in token])
    if voyage_dates:
        voyage_start = voyage_dates.split("/")[0]
        voyage_end = voyage_dates.split("/")[1]
        voyage_end = voyage_start[:-len(voyage_end)] + voyage_end
    job_id = person_id + "j" + str(job_counter)
    job_counter += 1
    job_row = [person_id, job_id, job, voyage_ship, voyage_start, voyage_end]
    return job_row

jobs_list = []
job_list = ["passenger", "apprentice", "seaman", "boatswain", "gunner's mate" "gunner", "midshipman", "capt's servant",
            "6th mate", "5th mate", "4th mate", "3rd mate", "2nd mate", "1st mate", 
            "quarter master", "purser", "surgeon", "surgeon's mate", "master", "lieutenant", "capt"]
for row in people_df.iterrows():
    person_id = row[1]["person_id"]
    info_tokens = str(row[1]["info"]).split(";")
    job_counter = 1
    for token in info_tokens:
        for job in job_list:
            job_string = job + " "
            if job_string in token.lower():
                if "approved" in token:
                    token = re.sub(r"\([^()]*approved[^()]*\)", "", token)
                # home as
                if ",home as" in token:
                    token_split = token.split(",home as")
                    for subtoken in token_split:
                        job_counter += 1
                        jobs_list.append(job_token_reader(subtoken, job_counter)) 
                # , - Several journeys, several ships
                elif "," in token:
                    token_split = token.split(",")
                    for subtoken in token_split:
                        job_counter += 1
                        jobs_list.append(job_token_reader(subtoken, job_counter))
                # X & X - One ship, several voyages
                if re.search(r"\d\s&\s\d", token):
                    token_split = []
                    subtoken = token.replace("&", "").split(" ")
                    non_date_split = [x for x in subtoken if not "/" in x]
                    non_date_string = " ".join(non_date_split).strip()
                    years_split = [x.strip(",").strip() for x in subtoken if "/" in x]
                    for year in years_split:
                        token_split.append(non_date_string + " " + year)
                    for subtoken in token_split:
                        job_counter += 1
                        jobs_list.append(job_token_reader(subtoken, job_counter)) 
                # Otherwise, add the single one
                else:
                    job_counter += 1
                    jobs_list.append(job_token_reader(token, job_counter))
jobs_df = pd.DataFrame(jobs_list)
jobs_df.rename(columns = {0: "person_id", 1: "job_id", 2: "job", 3: "voyage_ship", 4: "voyage_start", 5: "voyage_end"}, inplace = True)
print("Jobs done")

# Location table
# location_id   longitude   latitude
# location_id   float       float

location_list = []
locations_added_list = []
for location in calls_df.loc[calls_df["location"].notna()]["location"].tolist():
    for string in [" off ", " at ", " left "]:
        location = location.replace(string, "")
    location = re.sub(r"\([^()]*\)", "", location)
    location = location.strip()
    if location not in locations_added_list:
        locations_added_list.append(location)
        location_list.append([location, "calls"])
for location in ships_df.loc[ships_df["built_at"].notna()]["built_at"].tolist():
    if location not in locations_added_list:
        locations_added_list.append(location)
        location_list.append([location, "ships_built_at"])
for location in voyages_df.loc[voyages_df["destination"].notna()]["destination"].tolist():
    location = location.strip("From").strip()
    if " and " in location or "," in location or "&" in location:
        location_split = re.split(" and |,|&", location)
        for location in location_split:
            location = location.strip()
            if location not in locations_added_list:
                locations_added_list.append(location)
                location_list.append([location, "voyage_destinations"])
    if location not in locations_added_list:
        locations_added_list.append(location)
        location_list.append([location, "voyage_destinations"])
for location in people_df.loc[people_df["birth_location"].notna()]["birth_location"].tolist():
    if location not in locations_added_list:
        locations_added_list.append(location)
        location_list.append([location, "people_birth"])
for location in people_df.loc[people_df["baptised_city"].notna()]["baptised_city"].tolist():
    if location not in locations_added_list:
        locations_added_list.append(location)
        location_list.append([location, "people_baptised"])

locations_df = pd.DataFrame(location_list)
def location_id_creator(index):
    location_id = "l" + str(index + 1)
    return location_id
locations_df["location_id"] = locations_df.reset_index()["index"].apply(location_id_creator).drop(columns = ["index"])
locations_df.rename(columns = {0: "location", 1: "category"}, inplace = True)
locations_df = locations_df[["location_id", "location", "category"]]
print("Locations done")

# Referencing

# Jobs

voyages_merged_df = voyages_df.merge(ships_df, on = "ship_id")
voyages_merged_df = voyages_merged_df[["voyage_id", "name", "start", "end"]]
jobs_complete_df = pd.merge(jobs_df, voyages_merged_df, 
                            how = "left", 
                            left_on = ["voyage_ship", "voyage_start", "voyage_end"],
                            right_on = ["name", "start", "end"]
                            )
jobs_complete_df = jobs_complete_df[["person_id", "job_id", "job", "voyage_id"]]

# People: birth_location, baptised_city

def p_remover(person_id):
    number = str(person_id)[1:]
    number = int(number)
    return number

people_complete_df = people_df.sort_values("person_id")
people_birth_notna_df = people_df.loc[people_df["birth_location"].notna()]
people_birth_notna_df = pd.merge(people_birth_notna_df, locations_df,
                           how = "left",
                           left_on = "birth_location",
                           right_on = "location"
                           )
people_birth_na_df = people_df.loc[people_df["birth_location"].isna()]
people_birth_df = pd.concat([people_birth_notna_df, people_birth_na_df])
people_birth_df["sort"] = people_birth_df["person_id"].apply(p_remover)
people_birth_df = people_birth_df.sort_values(by = "sort").reset_index()
people_complete_df["birth_location"] = people_birth_df["location_id"]

people_baptised_notna_df = people_df.loc[people_df["baptised_city"].notna()]
people_baptised_notna_df = pd.merge(people_baptised_notna_df, locations_df,
                           how = "left",
                           left_on = "baptised_city",
                           right_on = "location"
                           )
people_baptised_na_df = people_df.loc[people_df["baptised_city"].isna()]
people_baptised_df = pd.concat([people_baptised_notna_df, people_baptised_na_df])
people_baptised_df["sort"] = people_baptised_df["person_id"].apply(p_remover)
people_baptised_df = people_baptised_df.sort_values(by = "sort").reset_index()
people_complete_df["baptised_city"] = people_baptised_df["location_id"]
people_complete_df.sort_index(inplace = True)

# Calls: location

calls_complete_df = pd.merge(calls_df, locations_df, 
                            how = "left", 
                            left_on = "location",
                            right_on = "location"
                            )
calls_complete_df["location"] = calls_complete_df["location_id"]
calls_complete_df = calls_complete_df[["ship_id", "voyage_id", "call_id", "raw", "year", "month", "day", "location", "special"]]

# Ships: built_by, built_at, owner

ships_complete_df = pd.merge(ships_df, locations_df, 
                            how = "left", 
                            left_on = "built_at",
                            right_on = "location"
                            )
ships_complete_df["built_at"] = ships_complete_df["location_id"]
ships_complete_df.drop(columns = ["location", "location_id", "category"], inplace = True)

# XXXX Add built_by to people

# XXXX Add owner to people

print("Referencing done")

# Automatic geocoding using Geonames

geocode_df = pd.read_csv(path.join(dir, "geocoding/geonames.csv"), sep = ";", encoding = "utf-8")

locations_list = locations_df["location"].tolist()
def geocoded_dict_creator(locations_list):
    geocoded_dict = {}
    for location_raw in locations_list:
        location = str(location_raw)
        location = re.sub(r"\[.+?\]|\(.+?\)|\{.+?\}", "", location)
        location = re.sub(r"[^a-zA-Z\s]+", "", location)
        location = location.lower().strip().replace("  ", " ")
        location = unidecode(location)
        location_split = [token for token in location.split(" ") if not token.isdigit()]
        location = " ".join(location_split)
        if len(location) > 2 and location not in geocoded_dict.keys():
            geocoded_dict[location] = [location_raw]
    return geocoded_dict
geocoded_dict = geocoded_dict_creator(locations_list)

#geocode_df = geocode_df.loc[geocode_df["Country Code"].isin(["PT"])]
geocode_df = geocode_df[["Name", "Coordinates", "Population", "Alternate Names", "Country Code"]]
geocode_df["name_code"] = geocode_df["Name"].str.lower().apply(unidecode)
geocode_df["Alternate Names"] = geocode_df["Alternate Names"].str.lower()
geocode_british_isles_df = geocode_df.loc[geocode_df["Country Code"].isin(["GB", "IE"])]
geocode_other_df = geocode_df.loc[~geocode_df["Country Code"].isin(["GB", "IE"])]

def geocoded_df_creator(geocoded_dict):
    location_counter = 0
    #success_counter = 0
    for city in geocoded_dict.keys():
        location_counter += 1
        search_string = str("," + city + ",")
        # Check in British Isles primary names
        if city in geocode_british_isles_df["name_code"].to_list():
            if len(geocoded_dict[city]) == 1:
                    coordinates = geocode_british_isles_df.loc[geocode_british_isles_df["name_code"] == city]["Coordinates"].values[0].split(", ")
                    geocoded_dict[city].append(coordinates[0])
                    geocoded_dict[city].append(coordinates[1])
                    #success_counter += 1
        # Check in other primary names
        elif city in geocode_other_df["name_code"].to_list():
            if len(geocoded_dict[city]) == 1:
                    coordinates = geocode_other_df.loc[geocode_other_df["name_code"] == city]["Coordinates"].values[0].split(", ")
                    geocoded_dict[city].append(coordinates[0])
                    geocoded_dict[city].append(coordinates[1])
                    #success_counter += 1
        # Otherwise check in all alternate names
        elif geocode_df["Alternate Names"].str.contains(search_string, na = False).any():
            coordinates = geocode_df.loc[geocode_df["Alternate Names"].str.contains(search_string, na = False)].sort_values("Population")["Coordinates"].values[0].split(", ")
            geocoded_dict[city].append(coordinates[0])
            geocoded_dict[city].append(coordinates[1])
            #success_counter += 1
        print("Geocoding done:", str((location_counter / len(geocoded_dict.keys()))*100)[:5], "%")
        #print("Geocoding done:", str((location_counter / len(geocoded_dict.keys()))*100)[:5], "% - success:", str((success_counter / location_counter)*100)[:5], "%")
    geocoded_df = pd.DataFrame.from_dict(geocoded_dict, orient = "index")
    geocoded_df = geocoded_df.reset_index().reset_index().rename(columns = {"level_0": "id", "index": "name_code", 0: "name", 1: "lat", 2: "lon"})
    geocoded_df = geocoded_df.loc[geocoded_df["lat"].notna()]
    return geocoded_df
geocoded_df = geocoded_df_creator(geocoded_dict)

# Manual annotation

locations_geocoded_df = pd.merge(locations_df, geocoded_df, 
                            how = "left", 
                            left_on = "location",
                            right_on = "name"
                            )
locations_geocoded_df = locations_geocoded_df[["location_id", "location", "category", "lat", "lon"]]
locations_annotate_df = locations_geocoded_df.loc[locations_geocoded_df["lat"].isna()]
locations_annotate_df.drop(columns = ["location_id"], inplace = True)
# Create annotate file if it doesn't exist yet
if not path.exists(dir + "/geocoding/annotate.csv"):
    pd.DataFrame.to_csv(locations_annotate_df, path.join(dir, "geocoding/annotate.csv"), encoding = "utf-8", sep = ";", index = False)
    locations_annotate_combined_df = locations_annotate_df
    locations_complete_df = locations_geocoded_df
# Otherwise, load locations that have been annotated there
else:
    locations_annotated_df = pd.read_csv(path.join(dir, "geocoding/annotate.csv"), encoding = "utf-8", sep = ";")
    locations_annotated_df = locations_annotated_df.loc[locations_annotated_df["lat"].notna()]
    #print(locations_annotated_df.head())
    #locations_annotated_df.drop(columns = ["category_x", "category_y"], inplace = True)
    locations_annotated_list = locations_annotated_df["location"].tolist()
    locations_annotate_df = locations_annotate_df.loc[~locations_annotate_df["location"].isin(locations_annotated_list)]
    #locations_annotate_df = pd.merge(
    #    locations_annotate_df, locations_df,
    #    how = "left",
    #    on = "location"
    #)
    locations_annotate_combined_df = pd.concat([locations_annotated_df, locations_annotate_df])
    pd.DataFrame.to_csv(locations_annotate_combined_df, path.join(dir, "geocoding/annotate.csv"), encoding = "utf-8", sep = ";", index = False)
    #locations_annotated_df.drop(columns = ["category_x", "category_y"], inplace = True)
    locations_annotated_df = pd.merge(
        locations_annotated_df, locations_df,
        how = "left",
        on = "location"
    )
    locations_annotated_df = locations_annotated_df[["location_id", "location", "category_x", "lat", "lon"]]
    locations_annotated_df.rename(columns = {"category_x": "category"}, inplace = True)
    #locations_annotated_df = locations_annotated_df[["location_id_x", "location", "category_x", "lat", "lon"]]
    #locations_annotated_df.rename(columns = {"location_id_x": "location_id", "category_x": "category"}, inplace = True)
    locations_complete_df = pd.concat([locations_annotated_df, locations_geocoded_df.loc[~locations_geocoded_df["location"].isin(locations_annotated_list)]], ignore_index = True)

# Some don't need any changes here

voyages_complete_df = voyages_df

# Save tables

ships_complete_df.to_csv(path.join(dir, "output/ships.csv"), index = False, sep = ";", encoding = "utf-8")
voyages_complete_df.to_csv(path.join(dir, "output/voyages.csv"), index = False, sep = ";", encoding = "utf-8")
calls_complete_df.to_csv(path.join(dir, "output/calls.csv"), index = False, sep = ";", encoding = "utf-8")
people_complete_df.to_csv(path.join(dir, "output/people.csv"), index = False, sep = ";", encoding = "utf-8")
jobs_complete_df.to_csv(path.join(dir, "output/jobs.csv"), index = False, sep = ";", encoding = "utf-8")
locations_complete_df.to_csv(path.join(dir, "output/locations.csv"), index = False, sep = ";", encoding = "utf-8")