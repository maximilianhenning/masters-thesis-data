import pandas as pd
from glob import glob
from os import path, makedirs
import re

dir = path.dirname(__file__)

# Voyages

# Classify lines
def line_classify(lines):
    lines_classed = []
    for line in lines:
        line_text = ""
        for char in line:
            if not char.isnumeric() or char in "()":
                line_text += char
        if line_text.isupper() and not "/" in line:
            line_class = "ship"
        # Either normal itinerary with - in the middle or one where only the end is known
        elif " - " in line or line.startswith("-"):
            line_class = "itinerary"
        elif str(line).startswith("Capt"):
            line_class = "captain"
        elif str(line[:4]).isalpha() and not "/" in line[:10]:
            line_class = "info"
        # Catch some of the ones starting with numbers as well
        elif "guns" in str(line) or "tons" in str(line):
            line_class = "info"
        # Catch the odd general reference or footnote as well
        elif str(line).startswith("See ") or str(line).startswith("*"):
            line_class = "info"
        elif str(line[:1]).isnumeric() and str(line[1] == " "):
            line_class = "voyage_id"
        elif str(line).startswith("L/"):
            line_class = "reference"
        else:
            line_class = "unclassed"
        lines_classed.append([line, line_class])
    return lines_classed

# Group lines into ship entries
def ship_creator(lines_classed):
    ships = {}
    for line in lines_classed:
        # If line is a ship's name, add to ships dict as key
        if line[1] == "ship":
            ship = line[0]
            # Start dict for ship
            ship_dict = {"info": []}
            ships[ship] = [ship_dict]
        # If info, add to ship dict
        if line[1] == "info":
            ship_dict["info"].append(line[0])
        # If unclassed, add to ship dict - probably better not to lose those lines
        if line[1] == "unclassed":
            ship_dict["info"].append(line[0])
        # If voyage ID, add to ship dict & start voyage dict
        if line[1] == "voyage_id":
            voyage = "voyage_" + line[0][0]
            voyage_info = line[0][2:]
            if "From" in voyage_info:
                voyage_time = voyage_info.split(" ")[-1]
                voyage_destination = voyage_info.split(" ")[:-1]
                voyage_destination = " ".join(voyage_destination)
            else:
                voyage_time = voyage_info.split(" ")[0]
                voyage_destination = voyage_info.split(" ")[1:]
                voyage_destination = " ".join(voyage_destination)
            if "/" in voyage_time:
                voyage_start = voyage_time[:4]
                voyage_end = voyage_time.split("/")[1]
                if len(voyage_end) == 1:
                    voyage_end = voyage_start[:3] + voyage_end
                else:
                    voyage_end = voyage_start[:2] + voyage_end
                voyage_time = [voyage_start, voyage_end]
            # Start or empty dict for voyage
            voyage_dict = {"time": voyage_time, "destination": voyage_destination, "reference": [], "captain": []}
            ship_dict[voyage] = voyage_dict
        # Add references
        if line[1] == "reference":
            voyage_dict["reference"].append(line[0])
        # Add captain
        if line[1] == "captain":
            voyage_dict["captain"] = line[0][5:]
        # Add itinerary
        if line[1] == "itinerary":
            voyage_dict["itinerary"] = line[0]
        ships[ship] = ship_dict
    # Convert to DataFrame
    df_ships = pd.DataFrame.from_dict(ships, orient = "index")
    return df_ships

# Wrangle each file
clean_file_list = glob(path.join(dir, "voyages_clean/*"))
for file in clean_file_list:
    file = file.split("\\")[-1].split(".")[0]
    with open(path.join(dir, "voyages_clean", file + ".txt"), "r") as input:
        text = input.read()
    lines = text.split("\n")
    lines_classed = line_classify(lines)
    df_line_classes = pd.DataFrame(lines_classed, columns = ["line", "class"])
    # Monitoring
    print("\n" + file)
    print(df_line_classes.loc[df_line_classes["class"] == "unclassed"])
    # Create ships from lines
    df_ships = ship_creator(lines_classed)
    df_ships = df_ships.reset_index().rename(columns = {"index": "name"})
    # Save to CSV
    if not path.exists(path.join(dir, "voyages_partial")):
        makedirs(path.join(dir, "voyages_partial"))
    df_ships.to_csv(path.join(dir, "voyages_partial", file + ".csv"), index = False, sep = ";")

# Combine files
df_list = []
partial_file_list = glob(path.join(dir, "voyages_partial/*"))
for file in partial_file_list:
    file = file.split("\\")[-1].split(".")[0]
    df = pd.read_csv(path.join(dir, "voyages_partial", file + ".csv"), sep = ";")
    df_list.append(df)
# Concatenate and drop old indexes
df_combined = pd.concat(df_list)
df_combined = df_combined.reset_index().drop(columns = ["index"])
# Convert ship ID from index to column
df_combined = df_combined.reset_index().rename(columns = {"index": "ship_id"})
def id_creator(ship_id):
    return "s" + str(ship_id + 1)
df_combined["ship_id"] = df_combined["ship_id"].apply(id_creator)
df_combined.to_csv(path.join(dir, "combined/voyages.csv"), index = False, sep = ";", na_rep = "nan")

# Officers

# Classify lines
def officer_classify(lines):
    lines_classed = []
    for line in lines:
        if re.search(r"\([^()]{4,}\)", line):
            line_class = "person"
        elif ";" in line:
            line_class = "info"
        elif ", " in line:
            line_class = "person"
            tokens = line.split(", ")
            if len(tokens) != 2:
                line_class = "info"
            for token in tokens:
                if len(token) > 20:
                    line_class = "info"
                if len(token.split(" ")) > 3:
                    line_class = "info"
        else:
            line_class = "info"
        lines_classed.append([line, line_class])
    return lines_classed

# Group lines into personal entries
def people_creator(lines_classed):
    people = {}
    person_counter = 0
    for line in lines_classed:
        if line[1] == "person":
            person_counter += 1
            person_line = line[0]
            people[person_counter] = [person_line]
            # Collect info lines
        elif line[1] == "info":
            if person_counter in people.keys():
                people[person_counter].append(line[0])
    # Convert to DataFrame
    people_df = pd.DataFrame.from_dict(people, orient = "index")
    return people_df

# Wrangle each file
clean_file_list = glob(path.join(dir, "officers_clean/*"))
for file in clean_file_list:
    file = file.split("\\")[-1].split(".")[0]
    with open(path.join(dir, "officers_clean", file + ".txt"), "r") as input:
        text = input.read()
    lines = text.split("\n")
    lines_classed = officer_classify(lines)
    df_line_classes = pd.DataFrame(lines_classed, columns = ["line", "class"])
    # Monitoring
    print("\n" + file)
    print(df_line_classes.loc[df_line_classes["class"] == "person"])
    # Create people from lines
    people_df = people_creator(lines_classed)
    print(people_df.head())
    # Save to CSV
    if not path.exists(path.join(dir, "officers_partial")):
        makedirs(path.join(dir, "officers_partial"))
    people_df.to_csv(path.join(dir, "officers_partial", file + ".csv"), index = False, sep = ";")

# Combine files
df_list = []
partial_file_list = glob(path.join(dir, "officers_partial/*"))
for file in partial_file_list:
    file = file.split("\\")[-1].split(".")[0]
    df = pd.read_csv(path.join(dir, "officers_partial", file + ".csv"), sep = ";")
    df_list.append(df)
# Concatenate and drop old indexes
df_combined = pd.concat(df_list)
df_combined = df_combined.reset_index().drop(columns = ["index"])
# Convert ship ID from index to column
df_combined = df_combined.reset_index().rename(columns = {"index": "person_id"})
def id_creator(ship_id):
    return "p" + str(ship_id + 1)
df_combined["person_id"] = df_combined["person_id"].apply(id_creator)
df_combined.to_csv(path.join(dir, "combined/people.csv"), index = False, sep = ";", na_rep = "nan")