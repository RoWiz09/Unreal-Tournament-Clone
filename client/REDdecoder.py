import json, ast

class REDFileError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class REDFile:
    def __init__(self, file_name:str):
        """
        Loads the data from a .red file. Useful for decoding game data that you want to encode.
        #### -- Parameters --
        > `file_name`: The name of the .red file (extension included).
        """
        with open(file_name) as REDFILE:
            REDfile = REDFILE.read()
            out = []
            list(map(lambda sect: out.append(int('0b'+sect,0)) if sect else None, REDfile.split('0b')))

            REDfile_contents = ""
            REDfile = out

            REDfile_contents = "".join(list(map(lambda sect : chr(int(((((sect*2)**(1/2))/2)+4))).replace("'","'"),REDfile)))

            REDfile:dict = ast.literal_eval(REDfile_contents.removeprefix("\"").removesuffix("\""))
            self.redfile = REDfile

    def get_location(self, file):
        """
            Returns the data from a location stored in the REDfile
            #### -- Parameters --
            > `file`: the file you want to get the data from
        """
        return self.redfile[file]

    def display_redfile(self):
        """
            Prints the REDfile to the console
        """
        print(self.redfile)
