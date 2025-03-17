from utils import networking
import OpenGL.GL as GL
import ctypes, glm
import numpy as np
import _thread
import time, random

class WorldRenderer:
    def __init__(self, verts : np.ndarray):
        self.verticies = (len(verts)//8)*3
        
        # Generate Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        # Bind VAO and VBO
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verts.nbytes, verts, GL.GL_STATIC_DRAW)

        # Position Attribute
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 8 * verts.itemsize, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV Attribute
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 8 * verts.itemsize, ctypes.c_void_p(3 * verts.itemsize))
        GL.glEnableVertexAttribArray(1)

        # Normal Attribute
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, 8 * verts.itemsize, ctypes.c_void_p(5 * verts.itemsize))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(0)

    def render(self, shader):
        model = glm.mat4x4(1.0)
        shader.SetMat4x4("model", model)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)

class player_renderer:
    def __init__(self, network : networking.NetworkClient, verts : np.ndarray, my_player = False):
        self.pos = glm.vec3(0,0,0)
        self.verticies = (len(verts)//8)*3
        self.me = my_player
        self.network = network

        self.test = random.random()
        
        # Generate Vertex Buffer Object (VBO) and Vertex Array Object (VAO)
        self.vbo = GL.glGenBuffers(1)
        self.vao = GL.glGenVertexArrays(1)

        # Bind VAO and VBO
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, verts.nbytes, verts, GL.GL_STATIC_DRAW)

        # Position Attribute
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 8 * verts.itemsize, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV Attribute
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 8 * verts.itemsize, ctypes.c_void_p(3 * verts.itemsize))
        GL.glEnableVertexAttribArray(1)

        # Normal Attribute
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, 8 * verts.itemsize, ctypes.c_void_p(5 * verts.itemsize))
        GL.glEnableVertexAttribArray(2)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        GL.glBindVertexArray(0)

        _thread.start_new_thread(self.send, ())

    def render(self, shader):
        if not self.me:
            model = glm.mat4x4(1.0)
            model = glm.translate(model, self.pos)
            shader.SetMat4x4("model", model)

            GL.glBindVertexArray(self.vao)
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.verticies)

    def send(self):
        while True:
            if self.me:
                packet = "playerPosTransformUpdate|"
                packet += str(self.pos.x)+"|"
                packet += str(self.pos.y)+"|"
                packet += str(self.pos.z)+","

                if len(packet.split("|")) == 4:
                    self.network.add_to_sending(packet.encode())

            time.sleep(0.01)
