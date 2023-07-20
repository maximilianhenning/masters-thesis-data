from os import path
from glob import glob
import re

dir = path.dirname(__file__)
file_list = glob(path.join(dir, "voyages_text", "*"))
occurences = 0
for file in file_list:
    file = file.split("\\")[-1].split(".")[0]
    with open(path.join(dir, "voyages_text", file + ".txt"), "r") as input:
        string = input.read()
    str_to_replace = " LSaugor "
    str_new = " Saugor "
    occurences_list = re.findall(str_to_replace, string)
    occurences += len(occurences_list)
    string = string.replace(str_to_replace, str_new)
    with open(path.join(dir, "voyages_text", file + ".txt"), "w") as output:
        output.write(string)
print("\"" + str_to_replace + "\" to \"" + str_new + "\":", occurences)