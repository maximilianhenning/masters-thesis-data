from os import path
from glob import glob
import re

dir = path.dirname(__file__)
file_list = glob(path.join(dir, "voyages_text", "*"))
for file in file_list:
    file = file.split("\\")[-1].split(".")[0]
    with open(path.join(dir, "voyages_text", file + ".txt"), "r") as input:
        string = input.read()
    str_to_replace = "Tellicheny"
    str_new = "Tellicherry"
    occurences = re.findall(str_to_replace, str)
    print(len(occurences))
    string.replace(str_to_replace, str_new)
    with open(path.join(dir, "voyages_text", file + ".txt"), "r") as output:
        output.write(string)