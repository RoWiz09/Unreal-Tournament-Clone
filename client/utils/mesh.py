import numpy as np

def load_obj(filename):
    vertices = []
    tex_coords = []
    normals = []
    faces = []

    with open(filename, "r") as file:
        for line in file:
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

    triangles = []
    for face in faces:
        triangle = [vertices[face[i][0] - 1] for i in range(3)]  # Get triangle vertices
        triangles.append(triangle)

    return np.array(out, dtype=np.float32), triangles