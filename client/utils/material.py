import OpenGL.GL as gl
import numpy as np
import glm, utils.shader as shader
import PIL.Image

class Material:
    def __init__(self, color : glm.vec4, texture : PIL.Image.Image, shader_prog : shader.ShaderProgram):
        self.col = color
        self.shader_prog = shader_prog
        self.img = texture

        self.tex_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex_id)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        tex_data = np.array(list(texture.getdata()),np.int16)
        format = gl.GL_RGBA if self.img.mode == 'RGBA' else gl.GL_RGB
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.img.size[0], self.img.size[1],
                    0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, tex_data)
       

    def apply(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.tex_id)

        self.shader_prog.Use()
        self.shader_prog.SetVec4("color", self.col)
