from utils import networking
from utils import material
from utils import renderer
from utils import shader
from utils import camera
import OpenGL.GL as gl
import _thread, ast
import glfw, time
import PIL.Image
import glm, PIL

class window:
    def __init__(self, res : tuple):
        glfw.init()
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        window = glfw.create_window(*res, "Real Tournament - Ghost game lore may be included!", None, None)
        glfw.make_context_current(window)

        gl.glClearColor(100/255, 100/255, 255/255, 255/255)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

        self.window = window

        self.to_create = []

        self.network_player_renderers : list[renderer.player_renderer] = []

        self.network = networking.NetworkClient(self, renderer.player_renderer)
        
        self.voted = False
        while True:
            if self.network.get_server_state() == networking.server_states.in_game:
                map_verts, self.light_data = self.network.request_map()
                break

            else:
                if not self.voted:
                    maps = self.network.get_maps()
                    voted_map = input("what is your map vote? Your choices are: %s "%maps.removesuffix(",").replace(".gltf","").replace(",",", ").replace("'",""))
                    if voted_map+".gltf" in ast.literal_eval("["+maps+"]"):
                        print("Voted for %s"%voted_map)
                        self.voted = True
                        self.network.vote_on_map(voted_map+".gltf")


        _thread.start_new_thread(self.network.start_reciving, (renderer.player_renderer,))
        
        self.map = renderer.WorldRenderer(map_verts)
        self.shader = shader.ShaderProgram("shaders\\vertex.glsl", "shaders\\fragment.glsl")
        self.camera = camera.camera()
        self.player_object = renderer.player_renderer(self.network, True)
        self.material = material.Material(glm.vec4(1,1,1,1), PIL.Image.open(".\\container.png"), self.shader)

        self.last_time = time.time()


        window_size = glfw.get_window_size(self.window)
        glfw.set_cursor_pos(self.window, window_size[0]/2, window_size[1]/2)

    def update(self):
        glfw.poll_events()

        cur_time = time.time()
        deltatime = cur_time-self.last_time
        self.last_time = cur_time

        mx, my = glfw.get_cursor_pos(self.window)
        self.camera.process_keyboard(deltatime)
        window_size = glfw.get_window_size(self.window)
        self.camera.process_mouse_movement(mx-window_size[0]/2, -my+window_size[1]/2)
        glfw.set_cursor_pos(self.window, window_size[0]/2, window_size[1]/2)

        view = glm.lookAt(self.camera.position, self.camera.position + self.camera.front, self.camera.up)
        projection = glm.perspective(glm.radians(self.camera.zoom), window_size[0] / window_size[1], 0.1, 16384.0)

        self.shader.Use()
        self.shader.SetMat4x4("view", view)
        self.shader.SetMat4x4("projection", projection)

        gl.glViewport(0, 0, *glfw.get_window_size(self.window))

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

        self.material.apply()
        self.player_object.pos.x = self.camera.position.x
        self.player_object.pos.y = self.camera.position.y 
        self.player_object.pos.z = self.camera.position.z
        self.player_object.render(self.shader)
        self.shader.set_lights(self.light_data)
        self.map.render(self.shader)

        for player_renderer in self.network_player_renderers:
            if isinstance(player_renderer, renderer.player_renderer):
                player_renderer.render(self.shader)

        for player in self.to_create:
            self.network_player_renderers[player[0]] = renderer.player_renderer(
                self.network
            )

            self.network_player_renderers[player[0]].pos.x = 0.0
            self.network_player_renderers[player[0]].pos.y = 0.0
            self.network_player_renderers[player[0]].pos.z = 0.0

        self.to_create.clear()

        glfw.swap_buffers(self.window)

    def get_window_state(self):
        return glfw.window_should_close(self.window)