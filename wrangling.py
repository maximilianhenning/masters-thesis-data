input = open("C:/Users/lorga/Uni/Thesis/Catalogue OCR/C.txt", "r")
text = input.read()
lines = text.split("\n")

for line in lines:
    line_text = ""
    for char in line:
        if not char.isnumeric() or char in "()":
            line_text += char
    if line_text.isupper() and not "/" in line:
        print(line)