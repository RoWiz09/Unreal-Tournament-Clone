import glm, keyboard, numpy as np
import OpenGL.GL as GL, ctypes

class camera:
    """
        A non-physical object in the game's scene. 
    """
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), up=glm.vec3(0.0, 1.0, 0.0), yaw=-90.0, pitch=0.0):
        """
            Creates and returns a new camera instance. 
            #### -- PARAMETERS -- 
            > `pos`: the camera's starting world position\n
            > `up`: the camera's up direction\n
            > `yaw`: the camera's starting yaw\n
            > `pitch`: the camera's starting pitch
        """
        self.position = position
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = up
        self.right = glm.vec3()
        self.world_up = up
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 5 
        self.sensitivity = 0.5
        self.zoom = 45.0
        self.update_vectors()

    def update_vectors(self):
        front = glm.vec3()
        front.x = np.cos(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        front.y = np.sin(glm.radians(self.pitch))
        front.z = np.sin(glm.radians(self.yaw)) * np.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def process_keyboard(self, delta_time):
        velocity = self.speed * delta_time
        if keyboard.is_pressed("w"):
            self.position += self.front * velocity
        if keyboard.is_pressed("s"):
            self.position -= self.front * velocity
        if keyboard.is_pressed("a"):
            self.position -= self.right * velocity
        if keyboard.is_pressed("d"):
            self.position += self.right * velocity

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.sensitivity
        y_offset *= self.sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_vectors()
        