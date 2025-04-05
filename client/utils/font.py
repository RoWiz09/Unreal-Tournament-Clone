import glm, PIL.Image as image
from utils.material import Material
from json import load
import numpy as np

def get_verts_custom_uv(uv):
    out = [
        # Positions  UVs
        0.0, 0.0,   uv[0][0],uv[1][1],  # Bottom-left
        1.0, 0.0,   uv[1][0],uv[1][1],  # Bottom-right
        0.0, 1.0,   uv[0][0],uv[0][1],  # Top-left

        0.0, 1.0,   uv[0][0],uv[0][1],  # Top-Left
        1.0, 0.0,   uv[1][0],uv[1][1],  # Bottom-right
        1.0, 1.0,   uv[1][0],uv[0][1],  # Top-right
    ]

    return out


class Font:
    def __init__(self, font_name:str, shader):
        self.font_mat = Material(glm.vec4(0,0,0,1),image.open(font_name), shader)

        with open(font_name.removesuffix(".png")+".json") as font_json:
            self.font_data = load(font_json)

    def get_text_verts(self, text:str):
        data = []
        for spec_char in self.font_data["special_binds"].keys():
            if spec_char in text:
                text.replace(spec_char, self.font_data["special_binds"][spec_char])

        for char in text:
            data.extend(get_verts_custom_uv(self.get_char_uvs(char)))

        return np.array(data, dtype=np.float32)

    def get_char_uvs(self, char:str):
        out = self.font_data["chars"][char]
        return out
    
    def apply(self, model:glm.mat4x4):
        self.font_mat.shader_prog.SetMat4x4("model", model)
        self.font_mat.apply()