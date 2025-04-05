from utils.material import Material
from utils.font import Font

import OpenGL.GL as GL
import numpy as np
import ctypes, glm

class ui_transform:
    def __init__(self, pos : glm.vec2, rot : glm.vec2, scale : glm.vec2):
        self.pos = pos
        self.rot = rot
        self.scale = scale

    def get_model_matrix(self):
        model = glm.mat4x4(0)
        model = glm.translate(model, glm.vec3(*self.pos, 1))

        model = glm.rotate(model, self.rot.x, (1,0,0))
        model = glm.rotate(model, self.rot.y, (0,0,1))

        model = glm.scale(model, glm.vec3(*self.scale, 0))

        return model

class panel:
    def __init__(self, verticies : np.ndarray, mat : Material, ui_transform:ui_transform):
        self.mat = mat

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

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)

class text:
    def __init__(self, transform:ui_transform, text:str, font:Font, ):
        self.font = font

        self.transform = transform
        
        verticies = font.get_text_verts(text)

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
        self.font.apply(self.transform.get_model_matrix())

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)