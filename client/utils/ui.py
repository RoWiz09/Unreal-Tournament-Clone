from utils.material import Material
from utils.font import Font
from utils import global_vars

import OpenGL.GL as GL
import numpy as np
import ctypes, glm

class anchors:
    top_left = (0,0)
    top_center = (0,1)
    top_right = (0,2)

    middle_left = (1,0)
    middle_center = (1,1)
    middle_right = (1,2)

    bottom_left = (2,0)
    bottom_center = (2,1)
    bottom_right = (2,2)

class ui_transform:
    def __init__(self, pos : glm.vec2, rot : glm.vec2, scale : glm.vec2, anchor:anchors = anchors.top_left):
        self.pos = glm.vec2(pos.x, pos.y)
        self.rot = rot
        self.scale = scale
        self.anchor = anchor

    def get_model_matrix(self, my_size:list):
        model = glm.mat4x4(1)
        #my_size[0] /= global_vars.window_size[0]
        #my_size[1] /= global_vars.window_size[1]
        # Top row anchors
        fin_pos = [self.pos.x/global_vars.window_size[0], self.pos.y/global_vars.window_size[1]]
        if self.anchor == anchors.top_center:
            fin_pos = [1+self.pos.x/global_vars.window_size[0], self.pos.y/global_vars.window_size[1]]
        elif self.anchor == anchors.top_right:
            fin_pos = [2-self.pos.x/global_vars.window_size[0]-my_size[0]/global_vars.window_size[0]*2, self.pos.y/global_vars.window_size[1]]

        # Middle row anchors
        elif self.anchor == anchors.middle_left:
            fin_pos = [self.pos.x/global_vars.window_size[0], -1-self.pos.y/global_vars.window_size[1]]
        elif self.anchor == anchors.middle_center:
            fin_pos = [1+self.pos.x/global_vars.window_size[0], -1-self.pos.y/global_vars.window_size[1]]
        elif self.anchor == anchors.middle_right:
            fin_pos = [2-self.pos.x/global_vars.window_size[0]-my_size[0]/global_vars.window_size[0]*2, -1-self.pos.y/global_vars.window_size[1]]

        # Bottom row anchors
        elif self.anchor == anchors.bottom_left:
            fin_pos = [self.pos.x/global_vars.window_size[0], -2+self.pos.y/global_vars.window_size[1]+my_size[1]/global_vars.window_size[1]*2]
        elif self.anchor == anchors.bottom_center:
            fin_pos = [1+self.pos.x/global_vars.window_size[0], -2+self.pos.y/global_vars.window_size[1]+my_size[1]/global_vars.window_size[1]*2]
        elif self.anchor == anchors.bottom_right:
            fin_pos = [2-self.pos.x/global_vars.window_size[0]-my_size[0]/global_vars.window_size[0]*2, -2+self.pos.y/global_vars.window_size[1]+my_size[1]/global_vars.window_size[1]*2]

        model = glm.translate(model, glm.vec3(*fin_pos, 1))

        model = glm.rotate(model, self.rot.x, (1,0,0))
        model = glm.rotate(model, self.rot.y, (0,0,1))

        model = glm.scale(model, glm.vec3(*self.scale, 1))

        return model
    
class textlike:
    def __init__(self, text:str, font_size:int=28, color:glm.vec4=glm.vec4(0,0,0,1)):
        self.text = text
        self.size = font_size
        self.color = color

class panel:
    def __init__(self, verticies : np.ndarray, mat : Material, transform:ui_transform):
        self.mat = mat
        self.transform = transform

        self.size = [verticies.data[0]-verticies.data[8], verticies.data[1]-verticies.data[9]]

        self.verticies = (len(verticies)//4)*2
        # Generate Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        # Bind VAO and VBO
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verticies.nbytes, verticies, GL.GL_STATIC_DRAW)

        # Position Attribute
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * verticies.itemsize, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV Attribute
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * verticies.itemsize, ctypes.c_void_p(2 * verticies.itemsize))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(0)

    def render(self):
        self.mat.apply()
        self.mat.shader_prog.SetMat4x4("model",self.transform.get_model_matrix(self.size))

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)

class text:
    def __init__(self, text:textlike, font : Font, transform:ui_transform):
        self.font = font
        self.text = text


        self.transform = transform

        verticies = font.get_text_verts(self.text.text, self.text.size)
        self.size = [verticies.data[len(verticies.data)-4], verticies.data[len(verticies.data)-7]]

        self.verticies = (len(verticies)//4)*2
        # Generate Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        # Bind VAO and VBO
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verticies.nbytes, verticies, GL.GL_STATIC_DRAW)

        # Position Attribute
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * verticies.itemsize, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV Attribute
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * verticies.itemsize, ctypes.c_void_p(2 * verticies.itemsize))
        GL.glEnableVertexAttribArray(1)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(0)

    def render(self):
        self.font.apply(self.transform.get_model_matrix(self.size), self.text.color)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)