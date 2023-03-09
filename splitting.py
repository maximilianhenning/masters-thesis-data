import pandas as pd

path = "C:/Users/lorga/Uni/Thesis/Data/"
df_combined = pd.read_csv(path + "combined.csv")

# Ships table
# ship_id   tons    guns    crew    built_by    info
# ship_id   string  string  string  string      string

# Voyages table
# voyage_id     ship    start   end     destination reference   captain         itinerary
# voyage_id     ship_id string  string  place_id    string      employee_id     place_id, string

# Employees table
# employee_id   owner   captain
# employee_id   ship_id voyage_id

# Places table
# place_id  longitude   latitude
# place_id  string      string