import numpy as np

def get_cube():
    verts = np.array([
        # Face y+ (Top)
        1.0, 1.0, 0.0,   1.0, 0.0,  0.0, 1.0, 0.0,  # Bottom-right
        0.0, 1.0, 0.0,   0.0, 0.0,  0.0, 1.0, 0.0,  # Bottom-left
        0.0, 1.0, 1.0,   0.0, 1.0,  0.0, 1.0, 0.0,  # Top-left
        1.0, 1.0, 1.0,   1.0, 1.0,  0.0, 1.0, 0.0,  # Top-right

        # Face y- (Bottom)
        0.0, 0.0, 1.0,   0.0, 1.0,  0.0, -1.0, 0.0,  # Top-left
        0.0, 0.0, 0.0,   0.0, 0.0,  0.0, -1.0, 0.0,  # Bottom-left
        1.0, 0.0, 0.0,   1.0, 0.0,  0.0, -1.0, 0.0,  # Bottom-right
        1.0, 0.0, 1.0,   1.0, 1.0,  0.0, -1.0, 0.0,  # Top-right

        # Face x+ (Right)
        1.0, 0.0, 1.0,   0.0, 1.0,  1.0, 0.0, 0.0,  # Top-left
        1.0, 0.0, 0.0,   0.0, 0.0,  1.0, 0.0, 0.0,  # Bottom-left
        1.0, 1.0, 0.0,   1.0, 0.0,  1.0, 0.0, 0.0,  # Bottom-right
        1.0, 1.0, 1.0,   1.0, 1.0,  1.0, 0.0, 0.0,  # Top-right

        # Face x- (Left)
        0.0, 1.0, 0.0,   1.0, 0.0,  -1.0, 0.0, 0.0,  # Bottom-right
        0.0, 0.0, 0.0,   0.0, 0.0,  -1.0, 0.0, 0.0,  # Bottom-left
        0.0, 0.0, 1.0,   0.0, 1.0,  -1.0, 0.0, 0.0,  # Top-left
        0.0, 1.0, 1.0,   1.0, 1.0,  -1.0, 0.0, 0.0,  # Top-right

        # Face z+ (Front)
        0.0, 1.0, 1.0,   1.0, 0.0,  0.0, 0.0, 1.0,  # Bottom-right
        0.0, 0.0, 1.0,   0.0, 0.0,  0.0, 0.0, 1.0,  # Bottom-left
        1.0, 0.0, 1.0,   0.0, 1.0,  0.0, 0.0, 1.0,  # Top-left
        1.0, 1.0, 1.0,   1.0, 1.0,  0.0, 0.0, 1.0,  # Top-right

        # Face z- (Back)
        1.0, 0.0, 0.0,   0.0, 1.0,  0.0, 0.0, -1.0,  # Top-left
        0.0, 0.0, 0.0,   0.0, 0.0,  0.0, 0.0, -1.0,  # Bottom-left
        0.0, 1.0, 0.0,   1.0, 0.0,  0.0, 0.0, -1.0,  # Bottom-right
        1.0, 1.0, 0.0,   1.0, 1.0,  0.0, 0.0, -1.0,  # Top-right

    ], dtype=np.float32)

    return verts

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
                    print(f"Skipping polygon with {len(face)} vertices (not supported)")

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

    return np.array(out, dtype=np.float32)