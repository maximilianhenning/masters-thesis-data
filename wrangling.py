import pandas as pd
from glob import glob

path = "C:/Users/lorga/Uni/Thesis/Data"
file_list = glob(path + "/Clean/*")

for file in file_list:
    file = file.split("\\")[-1].split(".")[0]
    with open(path + "/Clean/" + file + ".txt", "r") as input:
        text = input.read()
    lines = text.split("\n")

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
            elif " - " in line:
                line_class = "itinerary"
            elif str(line).startswith("Capt"):
                line_class = "captain"
            elif str(line[:4]).isalpha() and not "/" in line[:10]:
                line_class = "info"
            elif str(line[:1]).isnumeric() and str(line[1] == " "):
                line_class = "voyage_id"
            elif str(line).startswith("L/"):
                line_class = "reference"
            else:
                line_class = "unclassed"
            lines_classed.append([line, line_class])
        return lines_classed
    lines_classed = line_classify(lines)

    df_line_classes = pd.DataFrame(lines_classed, columns = ["line", "class"])
    print(file)
    print(df_line_classes.value_counts("class"))
    print(df_line_classes.loc[df_line_classes["class"] == "unclassed"])

    # Split lines into ship entries
    def ship_creator(lines_classed):
        ships = {}
        for line in lines_classed:
            #print(line)
            # If line is a ship's name, add to ships dict as key
            if line[1] == "ship":
                ship = line[0]
                # Start or empty dict for ship
                ship_dict = {"info": []}
                ships[ship] = [ship_dict]
            # If info, add to ship dict
            if line[1] == "info":
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
        # Convert to dictionary
        df_ships = pd.DataFrame.from_dict(ships, orient = "index")
        return df_ships
    df_ships = ship_creator(lines_classed)

    df_ships.to_csv(path + "/Output/" + file + ".csv")