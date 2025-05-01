# Multithreading import
from _thread import start_new_thread

# Server imports
from server import networking as net_server

# Client imports
from client import menuhandler as menus
from client import global_vars
from client import networking
from client import REDdecoder
from client import input_lib
from client import material
from client import renderer
from client import shader
from client import camera
from client import chat
from client import font
from client import ui

# Other assorted imports
import OpenGL.GL as gl
import _thread, ast
import numpy as np
import glfw, time
import glm, PIL
import random
import math

class window:
    def __init__(self, res : tuple = None):
        self.game_assets = REDdecoder.REDFile("gamedata.red")

        glfw.init()
        
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if res:
            window = glfw.create_window(*res, "Real Tournament - Ghost game lore may be included!", None, None)
        else:
            window = glfw.create_window(*glfw.get_monitor_workarea(glfw.get_primary_monitor())[2:4], "Real Tournament - Ghost game lore may be included!", None, None)
            glfw.set_window_pos(window, 0, 0)
        glfw.make_context_current(window)

        gl.glClearColor(100/255, 100/255, 255/255, 255/255)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.window = window
        global_vars.window = window

        self.to_create = []
        self.chat_to_create = []

        self.network_player_renderers : list[renderer.player_renderer] = []

        self.ui_shader = shader.ShaderProgram(self.game_assets.get_location("ui_vert.glsl"), self.game_assets.get_location("ui_frag.glsl"))
        self.font = font.Font(self.game_assets.get_location("fontatlas.json"), self.game_assets.get_location("fontatlas.png"), self.ui_shader)
        
        self.voted = False
        self.window_size = glfw.get_window_size(window)
        global_vars.window_size = self.window_size
        test_mat_ui = material.Material(glm.vec4(1,1,1,1), self.game_assets.get_location("container.png"), self.ui_shader)

        self.menus = {
            "main":menus.menu([
                ui.button(
                    ui.textlike("Host Lobby", color=glm.vec4(1,1,1,1)),
                    self.font,
                    test_mat_ui,
                    ui.ui_transform(
                        glm.vec2(0, 0),
                        glm.vec2(0, 0),
                        glm.vec2(1, 1),
                        ui.anchors.top_left
                    ),
                    self.host_server
                ),
                ui.button(
                    ui.textlike("Join Lobby", color=glm.vec4(1,1,1,1)),
                    self.font,
                    test_mat_ui,
                    ui.ui_transform(
                        glm.vec2(0, -200),
                        glm.vec2(0, 0),
                        glm.vec2(1, 1),
                        ui.anchors.top_left
                    ),
                    self.connect_to_server,
                    "127.0.0.1",
                    42069
                )
            ]),
            "chat":menus.menu([
                ui.panel(
                    np.array([
                            self.window_size[0]/3, self.window_size[1]/2, 1.0, 1.0,  # top-right
                            self.window_size[0]/3, 0, 1.0, 0.0,  # bottom-right
                            0, 0, 0.0, 0.0,  # bottom-left

                            0, self.window_size[1]/2, 0.0, 1.0,   # top-left
                            self.window_size[0]/3, self.window_size[1]/2, 1.0, 1.0,  # top-right
                            0, 0, 0.0, 0.0,  # bottom-left
                        ], dtype=np.float32),
                    test_mat_ui,
                    ui.ui_transform(
                        glm.vec2(0, 0),
                        glm.vec2(0, 0),
                        glm.vec2(1, 1),
                        ui.anchors.bottom_left
                ))]
            )
        }

        self.menuhandler = menus.menuHandler(self.menus)
        
        self.shader = shader.ShaderProgram(self.game_assets.get_location("vertex.glsl"), self.game_assets.get_location("fragment.glsl"))
        
        self.camera = camera.camera()

        self.material = material.Material(glm.vec4(1,1,1,1), self.game_assets.get_location("container.png"), self.shader)

        self.last_time = time.time()

        window_size = glfw.get_window_size(self.window)
        glfw.set_cursor_pos(self.window, window_size[0]/2, window_size[1]/2)

        self.in_main_menu = True
        self.in_game = False

    def update(self):
        glfw.poll_events()

        cur_time = time.time()
        deltatime = cur_time-self.last_time
        self.last_time = cur_time

        window_size = glfw.get_window_size(self.window)

        if self.window_size != window_size:
            self.window_size = window_size
            self.menuhandler.menus["chat"].elements[0].regen_mesh(np.array([
                            self.window_size[0]/3, self.window_size[1]/2, 1.0, 1.0,  # top-right
                            self.window_size[0]/3, 0, 1.0, 0.0,  # bottom-right
                            0, 0, 0.0, 0.0,  # bottom-left

                            0, self.window_size[1]/2, 0.0, 1.0,   # top-left
                            self.window_size[0]/3, self.window_size[1]/2, 1.0, 1.0,  # top-right
                            0, 0, 0.0, 0.0,  # bottom-left
                        ], dtype=np.float32))

        global_vars.window_size = self.window_size
        
        if self.in_game:
            mx, my = glfw.get_cursor_pos(self.window)
            self.camera.process_keyboard(deltatime)
            self.camera.process_mouse_movement(math.floor(mx-math.floor(self.window_size[0]/2)), math.floor(-my+math.floor(self.window_size[1]/2)))
            glfw.set_cursor_pos(self.window, self.window_size[0]/2, self.window_size[1]/2)

            view = glm.lookAt(self.camera.position, self.camera.position + self.camera.front, self.camera.up)
        projection = glm.perspective(glm.radians(self.camera.zoom), self.window_size[0] / self.window_size[1], 0.1, 16384.0)

        if self.in_game:
            self.shader.Use()
            self.shader.SetMat4x4("view", view)
            self.shader.SetMat4x4("projection", projection)

        projection = glm.ortho(0, self.window_size[0], self.window_size[1], 0, -1.0, 1.0)

        self.ui_shader.Use()
        self.ui_shader.SetMat4x4("projection", projection)

        gl.glViewport(0, 0, *glfw.get_window_size(self.window))

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)

        if self.in_game:
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
                self.game_assets.get_location("game_cube.obj"),
                self.network
            )

            self.network_player_renderers[player[0]].pos.x = 0.0
            self.network_player_renderers[player[0]].pos.y = 0.0
            self.network_player_renderers[player[0]].pos.z = 0.0

        self.to_create.clear()

        # Disable GL_DEPTH_TEST for UI transparency
        gl.glDisable(gl.GL_DEPTH_TEST)

        # Render all required UI elements
        input_lib.handle_inputs(self.window)

        if self.in_main_menu:
            self.menuhandler.render_menu_name("main")
        else:
            self.menuhandler.render_menu_name("chat")
            chat.handle_input(self)

        # Update the window and enable GL_DEPTH_TEST for 3d rendering
        glfw.swap_buffers(self.window)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # Update the chat menu
        for msg in self.chat_to_create:
            for message in self.menuhandler.menus["chat"].elements:
                if isinstance(message, ui.text):
                    message.transform.pos.y += self.font.get_height(msg, 14)
            self.menuhandler.menus["chat"].elements.append(
            ui.text(
                ui.textlike(
                    msg, 
                    14
                ), 
                self.font, 
                ui.ui_transform(
                    glm.vec2(0,0), 
                    glm.vec2(0,0), 
                    glm.vec2(1,1), 
                    ui.anchors.bottom_left
                )
            )
        )
        self.chat_to_create.clear()

    def get_window_state(self):
        return glfw.window_should_close(self.window)
    
    def create_chat_msg(self, msg_contents:str):
        self.chat_to_create.append(msg_contents)

    def host_server(self, port:int=42069):
        server = net_server.Server(port=port)
        start_new_thread(server.update, ())

        self.connect_to_server("127.0.0.1", port=42069)

    def connect_to_server(self, ip_addr:str, port:int=42069):
        self.network = networking.NetworkClient(self, renderer.player_renderer, ip_addr, port)
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

        if self.network.team == "Blue" and len(self.network.blue_spawnpoints) > 0:
            random.choice(self.network.blue_spawnpoints).spawn(self.camera)

        elif not self.network.team == "Blue" and len(self.network.red_spawnpoints) > 0:
            random.choice(self.network.red_spawnpoints).spawn(self.camera)

        self.player_object = renderer.player_renderer(self.game_assets.get_location("game_cube.obj"), self.network, True)

        self.in_main_menu = False
        self.in_game = True