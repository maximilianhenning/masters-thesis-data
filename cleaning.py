from glob import glob

path = "C:/Users/lorga/Uni/Thesis/Data/"
file_list = glob(path + "Text/*")

for file in file_list:
    file = file.split("\\")[-1].split(".")[0]
    with open(path + "Text/" + file + ".txt", "r") as input:
        text = input.read()
    lines = text.split("\n")

    def cleaner(lines):
        lines_cleaned = []
        for line in lines:
            line = line.strip()
            # Clean characters: dot to line etc.
            line = line.replace("\t", " ")
            # Line break before L/MAR
            if "L/MAR" in line[5:]:
                line_split = line.split("L/MAR")
                # If there was something in front of L/MAR, add that back in
                if line_split[0]:
                    lines_cleaned.append(line_split[0])
                # Add in L/MAR line
                for line_broken in line_split[1:]:
                    lines_cleaned.append("L/MAR" + line_broken)
            # Line break before Capt
            elif "Capt" in line[5:]:
                line_split = line.split("Capt")
                lines_cleaned.append(line_split[0])
                lines_cleaned.append("Capt" + line_split[-1])
            # Line break before voyage ID
            elif "1 1" in line[5:]:
                print(line)
                line_split = line.split("1 1")
                line_split[1] = "1 1" + line_split[1]
                print(line_split[0] + "\n" + line_split[1])
                lines_cleaned.append(line_split[0])
                lines_cleaned.append(line_split[1])
            elif "1 From" in line[5:]:
                print(line)
                line_split = line.split("1 From")
                line_split[1] = "1 From" + line_split[1]
                print(line_split[0] + "\n" + line_split[1])
                lines_cleaned.append(line_split[0])
                lines_cleaned.append(line_split[1])
            # Remove XXXX see XXXX lines
            elif " see " in line:
                if line.replace(" see ", "").isupper():
                    pass
                else:
                    lines_cleaned.append(line)
            # Finally add working lines with content
            elif line:
                lines_cleaned.append(line)
        return lines_cleaned
    lines_cleaned = cleaner(lines)

    line_counter = 0
    for line in lines:
        line_counter += 1
    line_cleaned_counter = 0
    for line in lines_cleaned:
        line_cleaned_counter += 1
    print(file + "\nOriginal lines:", str(line_counter) + "\nCleaned lines:", str(line_cleaned_counter))

    with open(path + "Clean/" + file + ".txt", "w") as output:
        for line in lines_cleaned:
            output.write(line + "\n")