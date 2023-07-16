from os import path
import subprocess

dir = path.dirname(__file__)

subprocess.call(["python", path.join(dir, "scripts", "cleaning.py")])
print("Cleaning done")
subprocess.call(["python", path.join(dir, "scripts", "wrangling.py")])
print("Wrangling done")
subprocess.call(["python", path.join(dir, "scripts", "splitting.py")])
print("Splitting done")