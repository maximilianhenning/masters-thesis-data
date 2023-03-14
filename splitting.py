import pandas as pd
import ast

path = "C:/Users/lorga/Uni/Thesis/Data/"
df_combined = pd.read_csv(path + "/Output/combined.csv")

# Ships table
# ship_id   tons    guns    crew    type    built_by    built_year  Owner   info
# ship_id   string  string  string  string  string      string      string  string

df_ships = df_combined[["ship_id", "name", "info"]]

def feature_getter(info, feature):
    feature_result = info.split(feature)[0].strip().split(" ")[-1].replace("[\'", "")
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
df_ships.to_csv(path + "Output/ships.csv", index = False)

# Voyages table
# voyage_id     ship    start   end     destination reference   captain         itinerary
# voyage_id     ship_id string  string  place_id    string      employee_id     int, string, place_id

df_voyages_list = df_combined
df_voyages_list.drop(["name", "info"], axis = 1, inplace = True)
voyages_list = []
for row in df_voyages_list.iterrows():
    for x in range(1, 10):
        voyage_id = "voyage_" + str(x)
        if row[1][voyage_id]:
            voyages_list.append([row[0], x, row[1][voyage_id]])
df_voyages = pd.DataFrame(voyages_list)
df_voyages.rename(columns = {0: "ship_id", 1: "voyage_id", 2: "info"}, inplace = True)

def voyage_splitter(info):
    captain = "nan"
    start = "nan"
    end = "nan"
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
        
        # Captain
        captain = info["captain"]
    return pd.Series([start, end, captain])
    #return captain
df_voyages_expand = df_voyages["info"].apply(voyage_splitter)
df_voyages_expand.rename(columns = {0: "start", 1: "end", 2: "captain"}, inplace = True)
df_voyages = pd.concat([df_voyages, df_voyages_expand], axis = 1)
df_voyages.to_csv(path + "Output/voyages.csv", index = False)
print(df_voyages.head())

# Stops table
# ship_id   voyage_id   stop_id date    location
# ship_id   voyage_id   stop_id string  place_id    

# Employees table
# employee_id   owner   captain
# employee_id   ship_id voyage_id

# Places table
# place_id  longitude   latitude
# place_id  string      string

# Fill in IDs for relevant features in all tables
# XXXX