import json, ast, string
import PIL.Image

cols, rows = ast.literal_eval(input("how many rows and columns are there? (cols, rows) "))

font_uv = {"chars":{},"emojis":{}}

col = 0
row = 0

with PIL.Image.open(input("What is the file name? ")) as font_file:
    letter_size = (font_file.width/cols, font_file.height/rows)
    for char in string.ascii_uppercase+string.ascii_lowercase+" `"+"1234567890"+"-=[]\\;',./~!@#$%^&*()_+{}|:\"<>?"+input("what special characters are there? "):
        font_uv["chars"][char] = [[col*letter_size[0]/font_file.width, row*letter_size[1]/font_file.height],[(col+1)*letter_size[0]/font_file.width, (row+1)*letter_size[1]/font_file.height]]
        col += 1
        if col == cols:
            col = 0
            row += 1

with open("fontfile.json", "w") as font_data:
    json.dump(font_uv,font_data)
