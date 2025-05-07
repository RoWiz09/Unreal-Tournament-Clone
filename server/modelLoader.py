import json
import struct
import time

class spawnable:
    def __init__(self, verts:list):
        self.verts = verts

    def spawn(self):
        return "spawn|"+str(self.verts)

class light:
    def __init__(self, light_type: str, light_color: tuple, light_position: tuple, light_intensity: float):
        self.light_type = light_type
        self.light_col = light_color
        self.light_pos = light_position
        self.light_intensity = light_intensity

    def to_packet(self):
        packet = "light|"
        packet += str(self.light_type) + "|"
        packet += str(self.light_col) + "|"
        packet += str(self.light_intensity) + "|"
        packet += str(self.light_pos) + "\\"
        return packet
    
class spawnpoint:
    def __init__(self, pos:tuple, team:bool):
        """
            A player spawnpoint. 
            ## --- parameters ---
            > `pos`: The position of the spawnpoint in 3d space.\n
            > `team`: The team of the spawnpoint. False = Red, True = Blue
        """
        self.pos = pos
        self.team = team

    def to_packet(self):
        packet = "spawnpoint|"
        packet += str(self.pos)+"|"
        packet += str(self.team)+"\\"

        return packet
    
class weapon_spawnpoint:
    def __init__(self, pos:tuple, weapon_type:str, spawnRate:float, spawnOnLoad:bool=False):
        """
            A weapon spawnpoint. 
            ## --- parameters ---
            > `pos`: The position of the spawnpoint in 3d space.\n
            > `weapon`: The name of the weapon to spawn. Data for this weapon should be stored in the weapons directory.\n
            > `spawnRate`: How long it takes for the weapon to spawn.
            > `spawnOnLoad`: If the spawner should trigger on map load. Defaults to no.
        """
        self.pos = pos

        with open("weapons\\%s.json"%weapon_type) as weaponFile:
            self.weapon_data = json.load(weaponFile)

        self.weapon = spawnable(load_weapon_obj(self.weapon_data["weaponmodel"]))
        self.spawnRate = spawnRate
        self.spawnOnLoad = spawnOnLoad

        self.timer = time.time()
        self.timer_mod = 0

        self.has_weapon = False

    def update(self):
        if self.timer-self.timer_mod >= self.spawnRate:
            self.has_weapon = True

            self.timer_mod = self.timer

            packet = self.weapon.spawn()
            return packet
        
        else:
            self.timer = time.time()
            
class spawnpointError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def load_weapon_obj(file_name:str):
    with open("weapons\\"+file_name) as file:
        file_data = file.read()
        file.close()

    vertices = []
    tex_coords = []
    normals = []
    faces = []

    for line in file_data.split("\n"):
        parts = line.strip().split()
        if not parts:
            continue
        
        if parts[0] == "v":  # Vertex position
            vertices.append(tuple(map(float, parts[1:4])))

        elif parts[0] == "vt":  # Texture coordinates (UVs)
            tex_coords.append(tuple(map(float, parts[1:3])))  # Only take u, v

        elif parts[0] == "vn":  # Vertex normals
            normals.append(tuple(map(float, parts[1:4])))

        elif parts[0] == "f":  # Face indices
            face = []
            for p in parts[1:]:
                indices = p.split('/')
                
                v_idx = int(indices[0]) - 1
                vt_idx = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else None
                vn_idx = int(indices[2]) - 1 if len(indices) > 2 and indices[2] else None

                face.append((v_idx, vt_idx, vn_idx))
            if len(face) == 3:
                faces.append(face)
            elif len(face) == 4:  
                faces.append([face[0], face[1], face[2]])  # Triangle 1
                faces.append([face[0], face[2], face[3]])  # Triangle 2
            else:
                raise TypeError(f"ERROR: polygon with {len(face)} vertices not supported")

    out = []
    for face in faces:
        for v_idx, vt_idx, vn_idx in face:
            out.extend(vertices[v_idx])
            
            if vt_idx is not None and vt_idx < len(tex_coords):
                out.extend(tex_coords[vt_idx])
            else:
                out.extend([0.0, 0.0])

            if vn_idx is not None and vn_idx < len(normals):
                out.extend(normals[vn_idx])
            else:
                out.extend([0.0, 0.0, 1.0])

    return out

def load_gltf(filename:str):
    has_blue_spawnpoint = False
    has_red_spawnpoint = False

    with open("maps\\"+filename+".gltf", "r") as file:
        gltf = json.load(file)

    vertices = []
    tex_coords = []
    normals = []
    faces = []
    lights = []
    spawns = []
    weapon_spawns = []

    # Read binary buffer
    buffer_uri = gltf["buffers"][0]["uri"]
    with open("maps\\"+buffer_uri, "rb") as bin_file:
        buffer_data = bin_file.read()

    def extract_data(accessor_idx):
        accessor = gltf["accessors"][accessor_idx]
        buffer_view = gltf["bufferViews"][accessor["bufferView"]]
        start = buffer_view["byteOffset"]
        end = start + buffer_view["byteLength"]
        return buffer_data[start:end]

    for mesh in gltf["meshes"]:
        for primitive in mesh["primitives"]:
            # Load Vertices
            vertex_data = extract_data(primitive["attributes"]["POSITION"])
            for i in range(0, len(vertex_data), 12):
                x, y, z = struct.unpack("fff", vertex_data[i:i+12])
                vertices.append((x, y, z))

            # Load Normals (if available)
            if "NORMAL" in primitive["attributes"]:
                normal_data = extract_data(primitive["attributes"]["NORMAL"])
                for i in range(0, len(normal_data), 12):
                    nx, ny, nz = struct.unpack("fff", normal_data[i:i+12])
                    normals.append((nx, ny, nz))

            # Load Texture Coordinates (if available)
            if "TEXCOORD_0" in primitive["attributes"]:
                tex_data = extract_data(primitive["attributes"]["TEXCOORD_0"])
                for i in range(0, len(tex_data), 8):  # 2 floats per tex coord
                    u, v = struct.unpack("ff", tex_data[i:i+8])
                    tex_coords.append((u, v))

            # Load Indices
            index_data = extract_data(primitive["indices"])
            for i in range(0, len(index_data), 6):
                i1, i2, i3 = struct.unpack("HHH", index_data[i:i+6])
                faces.append((i1, i2, i3))

    if "extensions" in gltf and "KHR_lights_punctual" in gltf["extensions"]:
        light_data = gltf["extensions"]["KHR_lights_punctual"]["lights"]

        for node in gltf["nodes"]:
            if "extensions" in node and "KHR_lights_punctual" in node["extensions"]:
                light_index = node["extensions"]["KHR_lights_punctual"]["light"]
                light_info = light_data[light_index]

                light_type = light_info["type"]
                light_color = tuple(light_info.get("color", [1, 1, 1]))
                light_position = tuple(node.get("translation", [0, 0, 0]))
                light_intensity = light_info.get("intensity")

                lights.append(light(light_type, light_color, light_position, light_intensity))

            elif node["name"].startswith("PlayerSpawn"):
                if "extras" in node and "Team" in node["extras"]:
                    spawns.append(spawnpoint(node["translation"], "Blue" == node["extras"]["Team"]))
                    
                    if not has_blue_spawnpoint:
                        has_blue_spawnpoint = "Blue" == node["extras"]["Team"]
                    if not has_red_spawnpoint:
                        has_red_spawnpoint = "Red" == node["extras"]["Team"]
                else:
                    print(spawnpointError("The spawnpoint %s is invalid. Add extra data to validate it." % node["name"]))

            elif node["name"].startswith("WeaponSpawn"):
                if "extras" in node and "Weapon" in node["extras"]:
                    weapon_spawns.append(weapon_spawnpoint(node["translation"], node["extras"]["Weapon"], node["extras"]["Spawnrate"], node["extras"]["SpawnOnLoad"]))
                else:
                    print(spawnpointError("The weapon spawnpoint %s is invalid. Add extra data to validate it." % node["name"]))

    if not has_blue_spawnpoint:
        print(spawnpointError("The map %s is missing a blue spawnpoint. Strange behavior may occur."%filename.removesuffix(".gltf")))

    elif not has_red_spawnpoint:
        print(spawnpointError("The map %s is missing a red spawnpoint. Strange behavior may occur."%filename.removesuffix(".gltf")))

    # Flatten the vertex data for OpenGL
    out = []
    for face in faces:
        for v_idx in face:
            out.extend(vertices[v_idx])  # Add vertex position
            
            # Add texture coordinates if available
            if v_idx < len(tex_coords):
                out.extend(tex_coords[v_idx])
            else:
                out.extend([0.0, 0.0])  # Default UV if missing

            # Add normals if available
            if v_idx < len(normals):
                out.extend(normals[v_idx])
            else:
                out.extend([0.0, 0.0, 1.0])  # Default normal if missing

    return out, lights, spawns
