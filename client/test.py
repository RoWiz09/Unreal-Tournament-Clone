import PIL.Image

with PIL.Image.open("fontatlas.png") as atlas:
    print(list(atlas.getdata()))
    with open("help.txt","w") as file:
        file.write(str(list(atlas.getdata())))