from client.material import Material
from client.mesh import get_ui_quad
from glfw import get_cursor_pos
from client import global_vars
from client.font import Font

from client import input_lib as in_lib

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
    
    def get_colliding(self, my_size:list):
        fin_pos = [self.pos.x, -self.pos.y]
        if self.anchor == anchors.top_center:
            fin_pos = [(global_vars.window_size[0]/2)+self.pos.x, -self.pos.y]
        elif self.anchor == anchors.top_right:
            fin_pos = [global_vars.window_size[0]-self.pos.x-my_size[0], -self.pos.y]

        # Middle row anchors
        elif self.anchor == anchors.middle_left:
            fin_pos = [self.pos.x, global_vars.window_size[1]/2-self.pos.y]
        elif self.anchor == anchors.middle_center:
            fin_pos = [(global_vars.window_size[0]/2)+self.pos.x, global_vars.window_size[1]/2-self.pos.y]
        elif self.anchor == anchors.middle_right:
            fin_pos = [global_vars.window_size[0]-self.pos.x-my_size[0], global_vars.window_size[1]/2-self.pos.y]

        # Bottom row anchors
        elif self.anchor == anchors.bottom_left:
            fin_pos = [self.pos.x, global_vars.window_size[1]+self.pos.y+my_size[1]]
        elif self.anchor == anchors.bottom_center:
            fin_pos = [(global_vars.window_size[0]/2)+self.pos.x, global_vars.window_size[1]+self.pos.y-my_size[1]]
        elif self.anchor == anchors.bottom_right:
            fin_pos = [global_vars.window_size[0]-self.pos.x-my_size[0], global_vars.window_size[1]+self.pos.y-my_size[1]]

        mouse_pos = get_cursor_pos(global_vars.window)
        if mouse_pos[0] >= abs(fin_pos[0]) and mouse_pos[0] <= fin_pos[0] + self.scale.x*my_size[0]:
            if mouse_pos[1] >= abs(fin_pos[1])/2 and mouse_pos[1] <= abs(fin_pos[1])/2 + abs(self.scale.y*my_size[1]):
                return True

        return False

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

    def regen_mesh(self, verticies:np.ndarray):
        self.size = [verticies.data[0]-verticies.data[8], verticies.data[1]-verticies.data[9]]

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
        self.size = [verticies.data[len(verticies.data)-8], verticies.data[len(verticies.data)-7]]

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

class button:
    def __init__(self, textlike:textlike, font:Font, bg_mat:Material, transform:ui_transform, btn_command, *btn_command_args):
        self.text = text(textlike, font, transform)
        self.bg = panel(get_ui_quad(self.text.size), bg_mat, transform)

        self.click_event = btn_command
        self.click_event_args = btn_command_args

    def render(self):
        self.bg.render()
        self.text.render()
        
        if self.bg.transform.get_colliding(self.text.size):
            if in_lib.get_mouse_button_pressed(in_lib.mouseButtons.LEFT):
                self.click_event(*self.click_event_args)
