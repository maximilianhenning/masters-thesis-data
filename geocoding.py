import pandas as pd
from os import path
from glob import glob
import re
from unidecode import unidecode

dir = path.dirname(__file__)
geocode_df = pd.read_csv(path.join(dir, "geocoding/geonames.csv"), sep = ";", encoding = "utf-8")
locations_df = pd.read_csv(path.join(dir, "output/locations.csv"), sep = ";", encoding = "utf-8")

# Automatic geocoding using Geonames

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
geocode_df = geocode_df[["Name", "Coordinates", "Population", "Alternate Names"]]
geocode_df["name_code"] = geocode_df["Name"].str.lower().apply(unidecode)
geocode_df["Alternate Names"] = geocode_df["Alternate Names"].str.lower()

def geocoded_df_creator(geocoded_dict):
    location_counter = 0
    #success_counter = 0
    for city in geocoded_dict.keys():
        location_counter += 1
        search_string = str("," + city + ",")
        # Check in primary name
        if city in geocode_df["name_code"].to_list():
            if len(geocoded_dict[city]) == 1:
                    coordinates = geocode_df.loc[geocode_df["name_code"] == city]["Coordinates"].values[0].split(", ")
                    geocoded_dict[city].append(coordinates[0])
                    geocoded_dict[city].append(coordinates[1])
                    #success_counter += 1
        # Otherwise check in alternate names
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

# Manual annotation, XXXX rework so that manual annotation overrides automatic geocoding

locations_geocoded_df = pd.merge(locations_df, geocoded_df, 
                            how = "left", 
                            left_on = "location",
                            right_on = "name"
                            )
locations_geocoded_df = locations_geocoded_df[["location_id", "location", "category", "lat", "lon"]]

locations_annotate_df = locations_geocoded_df.loc[locations_geocoded_df["lat"].isna()]
# Create annotate file if it doesn't exist yet
if not path.exists(dir + "/geocoding/annotate.csv"):
    pd.DataFrame.to_csv(locations_annotate_df, path.join(dir, "geocoding/annotate.csv"), encoding = "utf-8", sep = ";", index = False)
    locations_annotate_combined_df = locations_annotate_df
# Otherwise, load locations that have been annotated there
else:
    locations_annotated_df = pd.read_csv(path.join(dir, "geocoding/annotate.csv"), encoding = "utf-8", sep = ";")
    locations_annotated_df = locations_annotated_df.loc[locations_annotated_df["lat"].notna()]
    # XXXX Rework this to use index instead of isin()
    locations_annotated_list = locations_annotated_df["location"].tolist()
    locations_annotate_df = locations_annotate_df.loc[~locations_annotate_df["location"].isin(locations_annotated_list)]
    locations_annotate_combined_df = pd.concat([locations_annotated_df, locations_annotate_df])
    pd.DataFrame.to_csv(locations_annotate_combined_df, path.join(dir, "geocoding/annotate.csv"), encoding = "utf-8", sep = ";", index = False)

locations_complete_df = pd.concat([locations_geocoded_df.loc[~locations_geocoded_df["location"].isin(locations_annotated_list)], locations_annotate_combined_df])
pd.DataFrame.to_csv(locations_complete_df, path.join(dir, "output/locations.csv"), encoding = "utf-8", sep = ";", index = False)