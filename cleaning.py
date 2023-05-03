from glob import glob
from os import path, makedirs
from PIL import Image
import pytesseract
import re

dir = path.dirname(__file__)
# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Voyages

def cleaner(lines):
    lines_cleaned = []
    for line in lines:
        line = line.strip()
        # Clean characters: dot to line etc.
        line = line.replace("\t", " ")
        line = line.replace("â€™", "\'")
        line = line.replace("â€˜", "\'")
        line = line.strip("â€¢")
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
        # Remove XXXX see XXXX lines
        elif " see " in line:
            # Check if everything but XXXX and XXXX are ship names
            if not line.replace(" see ", "").isupper():
                lines_cleaned.append(line)                
        # Finally add working lines with content
        elif line:
            lines_cleaned.append(line)
    return lines_cleaned

voyage_file_list = glob(path.join(dir, "voyages_text/*"))
overall_list = []
for file in voyage_file_list:
    file_title = file.split("\\")[-1].split(".")[0]
    with open(file, "r") as input:
        text = input.read()
    lines = text.split("\n")
    lines_cleaned = cleaner(lines)
    overall_list += lines_cleaned
    line_counter = 0
    for line in lines:
        line_counter += 1
    line_cleaned_counter = 0
    for line in lines_cleaned:
        line_cleaned_counter += 1
    print(file_title + "\nOriginal lines:", str(line_counter) + "\nCleaned lines:", str(line_cleaned_counter))
    if not path.exists(path.join(dir, "voyages_clean")):
        makedirs(path.join(dir, "voyages_clean"))
    with open(path.join(dir, "voyages_clean", file_title + ".txt"), "w") as output:
        for line in lines_cleaned:
            output.write(line + "\n")
with open(path.join(dir, "combined/voyages.txt"), "w") as output:
    for line in overall_list:
        output.write(line + "\n")

# Officers

def officer_clean(file_ocr):
    lines = file_ocr.split("\n")
    file_lines = []
    for line in lines:
        # Clean line
        clean_line = re.sub(r"\|", "", line)
        # Get lines with content
        if len(line) > 3:
            clean_line = clean_line.strip("â€˜")
            clean_line = clean_line.strip("i ")
            clean_line = clean_line.strip("’ ")
            clean_line = clean_line.replace("’", "\'")
            clean_line = clean_line.replace(":", ";")
            clean_line = clean_line.replace("Ist", "1st")
            clean_line = clean_line.replace("Sth", "5th")
            clean_line = clean_line.replace("Sad", "2nd")
            clean_line = clean_line.replace("mete", "mate")
            clean_line = clean_line.strip()
            file_lines.append(clean_line)
    return file_lines

officer_folder_list = glob(path.join(dir, "officers_png/*"))
if not path.exists(path.join(dir, "officers_ocr")):
    makedirs(path.join(dir, "officers_ocr"))
for folder in officer_folder_list: 
    folder_title = folder.split("\\")[-1].split(".")[0]
    if not path.exists(path.join(dir, "officers_ocr", folder_title + ".txt")):
        files = glob(folder + "/*")
        folder_ocr = []
        for file in files:
            file_ocr = pytesseract.image_to_string(Image.open(file))
            folder_ocr += file_ocr
        with open(path.join(dir, "officers_ocr", folder_title + ".txt"), "w") as output:
            for char in folder_ocr:
                output.write(char)
    print(folder_title + ": OCR done")
ocr_file_list = glob(path.join(dir, "officers_ocr/*"))
if not path.exists(path.join(dir, "officers_clean")):
    makedirs(path.join(dir, "officers_clean"))
for file in ocr_file_list: 
    file_title = file.split("\\")[-1].split(".")[0]
    with open(file, "r") as input:
        file_content = input.read()
    file_lines = officer_clean(file_content)
    with open(path.join(dir, "officers_clean", file_title + ".txt"), "w") as output:
        for line in file_lines:
            output.write(line + "\n")
    print(file_title + ": Cleaning done")