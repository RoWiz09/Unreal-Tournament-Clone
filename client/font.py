import glm, PIL.Image as image
from client.material import Material
from json import loads
import ast
import numpy as np
import time

def get_verts_custom_uv(uv, letter_offset_x:int, letter_offset_y:int, letter_size:int=28):
    out = [
        [
            (100/28*letter_size)+letter_offset_x, (100/28*letter_size)+letter_offset_y, uv[1][0], uv[1][1],  # top-right
            (100/28*letter_size)+letter_offset_x, 0+letter_offset_y, uv[1][0], uv[0][1],  # bottom-right
            0+letter_offset_x, 0+letter_offset_y, uv[0][0], uv[0][1],  # bottom-left

            0+letter_offset_x, (100/28*letter_size)+letter_offset_y, uv[0][0], uv[1][1],   # top-left
            (100/28*letter_size)+letter_offset_x, (100/28*letter_size)+letter_offset_y, uv[1][0], uv[1][1],  # top-right
            0+letter_offset_x, 0+letter_offset_y, uv[0][0], uv[0][1]  # bottom-left
        ]
    ]

    return out

class Font:
    def __init__(self, font_json_data:str, font_img_data:str, shader):
        self.font_mat = Material(glm.vec4(1,1,1,1),font_img_data, shader)

        self.font_data:dict = ast.literal_eval(font_json_data.replace("'''",""))

    def get_text_verts(self, text:str, font_size:int=28, max_width:int=None):
        data = []
        for spec_char in list(self.font_data["special_binds"].keys()):
            if spec_char in text:
                text=text.replace(spec_char, self.font_data["special_binds"][spec_char])

        letter_offset_x = 0
        letter_offset_y = 0
        for char in text:
            data.extend(*get_verts_custom_uv(self.get_char_uvs(char), letter_offset_x, letter_offset_y, font_size))
            letter_offset_x += (30/28)*font_size
            if max_width and max_width <= letter_offset_x:
                letter_offset_y += (70/28)*font_size
                letter_offset_x = 0

        return np.array(data, dtype=np.float32)

    def get_char_uvs(self, char:str):
        out = self.font_data["chars"][char]
        return out
    
    def apply(self, model:glm.mat4x4, color:glm.vec4):
        self.font_mat.apply()
        self.font_mat.shader_prog.SetMat4x4("model",model)
        self.font_mat.shader_prog.SetVec4("color",color)
    
    def get_height(self, text:str, font_size:int=28, max_width:int=None):
        for spec_char in list(self.font_data["special_binds"].keys()):
            if spec_char in text:
                text=text.replace(spec_char, self.font_data["special_binds"][spec_char])

        letter_offset_x = 0
        letter_offset_y = font_size+100/28*font_size
        for char in text:
            letter_offset_x += (30/28)*font_size
            if max_width and max_width <= letter_offset_x:
                letter_offset_y += (70/28)*font_size+100/28*font_size
                letter_offset_x = 0

        return letter_offset_y