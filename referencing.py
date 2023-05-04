import pandas as pd
from os import path

# Load tables

dir = path.dirname(__file__)
jobs_df = pd.read_csv(path.join(dir, "output/jobs.csv"), sep = ";", encoding = "utf-8")
calls_df = pd.read_csv(path.join(dir, "output/calls.csv"), sep = ";", encoding = "utf-8")
voyages_df = pd.read_csv(path.join(dir, "output/voyages.csv"), sep = ";", encoding = "utf-8")
people_df = pd.read_csv(path.join(dir, "output/people.csv"), sep = ";", encoding = "utf-8")
locations_df = pd.read_csv(path.join(dir, "output/locations.csv"), sep = ";", encoding = "utf-8")
ships_df = pd.read_csv(path.join(dir, "output/ships.csv"), sep = ";", encoding = "utf-8")

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

# Add built_by to people

# Add owner to people

# Save tables

jobs_complete_df.to_csv(path.join(dir, "output/jobs.csv"), index = False, sep = ";", encoding = "utf-8")
calls_complete_df.to_csv(path.join(dir, "output/calls.csv"), index = False, sep = ";", encoding = "utf-8")
people_complete_df.to_csv(path.join(dir, "output/people.csv"), index = False, sep = ";", encoding = "utf-8")
ships_complete_df.to_csv(path.join(dir, "output/ships.csv"), index = False, sep = ";", encoding = "utf-8")