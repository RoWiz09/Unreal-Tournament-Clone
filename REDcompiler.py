import argparse, os, math, json
import PIL.Image as im

args = argparse.ArgumentParser()
args.add_argument("--dir", type=str, required=True, dest="dir")
args = args.parse_args()

UNIMPLEMENTED_FILE_TYPES = ["bin"]
file_extension_warnings_given = []

print("compiling %s into a .red file"%args.dir.split("/")[-1])

def scan_dir(dir:str):
    out = []
    for dir_path, dir_name, file_name in os.walk(dir):
        for file in file_name:
            out.append(dir_path+"/"+file)

    return out

files = scan_dir(args.dir)

def compile_file(file:str):
    global file_extension_warnings_given
    out = []
    file_name = file.split("/")[-1]
    if file_name.split(".")[-1] == "png":
        img = im.open(file)

        im_data = list(img.getdata())
        im_data.append(img.width)
        im_data.append(img.height)

        return str(im_data)

    elif file_name.split(".")[-1] in UNIMPLEMENTED_FILE_TYPES:
        if file_name.split(".")[-1] not in file_extension_warnings_given:
            print("The .%s file extension is currently unsupported by this RED compiler." % file_name.split(".")[-1])
            file_extension_warnings_given.append(file_name.split(".")[-1])
            return

    else:
        with open(file) as f:
            try:
                data = f.read()
                f.close()

                return data

            except Exception as e:
                print("There was an error while reading the file %s, skipping file." % file_name)
                print(e)

                f.close()

                return


    return out

compiled_files = {}
REDfile = ""

for file in files:
    file_data = compile_file(file)
    if file_data:
        compiled_files[file.split("/")[-1]] = file_data

def mod_char(item):
    chars = map(lambda char : (((ord(char)-4)*2)**2)/2, item)

    redfile_contents = map(lambda ascii_rep:bin(int(ascii_rep)),list(chars))
    
    return "".join(list(redfile_contents))

char_map = map(mod_char,str(compiled_files))
REDfile = "".join(list(char_map))

with open(args.dir.removesuffix("\\")+".red", "w") as RED_file:
    RED_file.write(REDfile)
    RED_file.close()

