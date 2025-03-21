import pyassimp

# Load the FBX model
file_path = "test.fbx"
scene = pyassimp.load(file_path)

# Iterate over all meshes
for mesh in scene.meshes:
    print(f"Processing mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces.")

    # Iterate through faces
    for i, face in enumerate(mesh.faces):
        print(f"Face {i}: {face.indices}")  # Face indices

        # Retrieve actual vertex positions for this face
        face_vertices = [mesh.vertices[idx] for idx in face.indices]
        print(f"  Vertex positions: {face_vertices}")

# Cleanup to free memory
pyassimp.release(scene)
