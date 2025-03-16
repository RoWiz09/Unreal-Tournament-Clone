from OpenGL.GL import *
import glm, numpy as np

class ShaderProgram():
    def __init__(self, vertex_path, fragment_path):
        with open(vertex_path, "r") as file:
            vertexShaderSource = file.read()

        vertexShader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertexShader, vertexShaderSource)
        glCompileShader(vertexShader)

        if glGetShaderiv(vertexShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vertexShader))

        with open(fragment_path, "r") as file:
            fragmentShaderSource = file.read()

        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragmentShader, fragmentShaderSource)
        glCompileShader(fragmentShader)

        if glGetShaderiv(fragmentShader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(fragmentShader))

        shader_prog = glCreateProgram()
        glAttachShader(shader_prog, vertexShader)
        glAttachShader(shader_prog, fragmentShader)
        glLinkProgram(shader_prog)

        if glGetProgramiv(shader_prog, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(shader_prog))

        glUseProgram(shader_prog)

        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

        self.program = shader_prog

    def SetMat4x4(self, name, matrix):
        glUniformMatrix4fv(glGetUniformLocation(self.program, name), 1, GL_FALSE, glm.value_ptr(matrix))

    def SetVec3(self, name, value):
        glUniform3f(glGetUniformLocation(self.program, name), *value)

    def SetVec4(self, name, value : glm.vec4):
        glUniform4f(glGetUniformLocation(self.program, name), *value)

    def SetInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def SetFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)

    def set_lights(self, light_data):
        # Number of active lights
        num_lights = 1
        glUniform1i(glGetUniformLocation(self.program, "numLights"), num_lights)

        # Set light data in the shader
        for i, light in enumerate(light_data):
            glUniform3f(glGetUniformLocation(self.program, f"pointLights[{i}].position"), *light["position"])
            glUniform3f(glGetUniformLocation(self.program, f"pointLights[{i}].color"), *light["color"])
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].intensity"), light["intensity"])
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].constant"), light["constant"])
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].linear"), light["linear"])
            glUniform1f(glGetUniformLocation(self.program, f"pointLights[{i}].quadratic"), light["quadratic"])

    def Use(self):
        glUseProgram(self.program)