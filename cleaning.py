from glob import glob
from os import path, makedirs
from PIL import Image
import pytesseract
import re

dir = path.dirname(__file__)
# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Voyages

# Line cleaner function
def cleaner(lines):
    lines_cleaned = []
    # Iterate through lines
    for line in lines:
        # Clean lines
        line = line.strip()
        line = line.strip(">")
        line = line.strip("<")
        line = line.strip("^")
        line = line.strip("â€¢")
        line = line.replace("=", "-")
        line = line.replace("\t", " ")
        line = line.replace("â€™", "\'")
        line = line.replace("â€˜", "\'")
        # Add line breaks before L/MAR, which is always at the start of lines
        if "L/MAR" in line[5:]:
            line_split = line.split("L/MAR")
            # If there was something in front of L/MAR, add that back in
            if line_split[0]:
                lines_cleaned.append(line_split[0])
            # Add in L/MAR line
            for line_broken in line_split[1:]:
                lines_cleaned.append("L/MAR" + line_broken)
        # Add line break before Capt
        elif "Capt" in line[5:]:
            line_split = line.split("Capt")
            lines_cleaned.append(line_split[0])
            lines_cleaned.append("Capt" + line_split[-1])
        # Add line break before voyage ID
        elif "1 1" in line[5:]:
            line_split = line.split("1 1")
            line_split[1] = "1 1" + line_split[1]
            lines_cleaned.append(line_split[0])
            lines_cleaned.append(line_split[1])
        # Different way to write voyages
        elif "1 From" in line[5:]:
            line_split = line.split("1 From")
            line_split[1] = "1 From" + line_split[1]
            lines_cleaned.append(line_split[0])
            lines_cleaned.append(line_split[1])
        # Remove lines which refer to another ship entry
        elif " see " in line:
            # Check if everything but "see" is ship names
            if not line.replace(" see ", "").isupper():
                lines_cleaned.append(line)                
        # Finally add working lines with content
        elif line:
            lines_cleaned.append(line)
    return lines_cleaned

# Get files to be cleaned
voyage_file_list = glob(path.join(dir, "voyages_text/*"))
overall_list = []
# Apply function
for file in voyage_file_list:
    file_title = file.split("\\")[-1].split(".")[0]
    with open(file, "r") as input:
        text = input.read()
    lines = text.split("\n")
    lines_cleaned = cleaner(lines)
    # Monitoring
    overall_list += lines_cleaned
    line_counter = 0
    for line in lines:
        line_counter += 1
    line_cleaned_counter = 0
    for line in lines_cleaned:
        line_cleaned_counter += 1
    # Save files
    print(file_title + "\nOriginal lines:", str(line_counter) + "\nCleaned lines:", str(line_cleaned_counter))
    if not path.exists(path.join(dir, "voyages_clean")):
        makedirs(path.join(dir, "voyages_clean"))
    with open(path.join(dir, "voyages_clean", file_title + ".txt"), "w") as output:
        for line in lines_cleaned:
            output.write(line + "\n")
# Save combined file for debugging
with open(path.join(dir, "combined/voyages.txt"), "w") as output:
    for line in overall_list:
        output.write(line + "\n")

# Officers

# Officer line cleaner function
def officer_clean(file_ocr):
    lines = file_ocr.split("\n")
    file_lines = []
    # Iterate through lines
    for line in lines:
        # Clean line
        line = re.sub(r"\||\[|\]|\{|\}»", "", line)
        # Get lines with content
        if len(line) > 3:
            line = line.strip("â€˜")
            line = line.strip("i ")
            line = line.strip("’ ")
            line = line.replace("’", "\'")
            line = line.replace(":", ";")
            line = line.replace("lst", "1st")            
            line = line.replace("Ist", "1st")
            line = line.replace("Sth", "5th")
            line = line.replace("Sad", "2nd")
            line = line.replace("mete", "mate")
            line = line.strip()
            file_lines.append(line)
    return file_lines

# Glob files to be OCR's
officer_folder_list = glob(path.join(dir, "officers_png/*"))
overall_list = []
if not path.exists(path.join(dir, "officers_text")):
    makedirs(path.join(dir, "officers_text"))
# OCR files
for folder in officer_folder_list: 
    folder_title = folder.split("\\")[-1].split(".")[0]
    if not path.exists(path.join(dir, "officers_text", folder_title + ".txt")):
        files = glob(folder + "/*")
        folder_ocr = []
        for file in files:
            file_ocr = pytesseract.image_to_string(Image.open(file))
            folder_ocr += file_ocr
        with open(path.join(dir, "officers_text", folder_title + ".txt"), "w") as output:
            for char in folder_ocr:
                output.write(char)
    # Monitoring
    print(folder_title + ": OCR done")
# Clean files
ocr_file_list = glob(path.join(dir, "officers_text/*"))
if not path.exists(path.join(dir, "officers_clean")):
    makedirs(path.join(dir, "officers_clean"))
for file in ocr_file_list: 
    file_title = file.split("\\")[-1].split(".")[0]
    with open(file, "r") as input:
        file_content = input.read()
    file_lines = officer_clean(file_content)
    overall_list += file_lines
    # Save files
    with open(path.join(dir, "officers_clean", file_title + ".txt"), "w") as output:
        for line in file_lines:
            output.write(line + "\n")
    # Monitoring
    print(file_title + ": Cleaning done")
# Save combined file for debugging
with open(path.join(dir, "combined/persons.txt"), "w") as output:
    for line in overall_list:
        output.write(line + "\n")