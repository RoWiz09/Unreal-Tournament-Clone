import glm

class colliderTypes:
    normal_collider = 0
    trigger_collider = 1

class transform:
    def __init__(self, pos : glm.vec3, rot : glm.vec3, scale : glm.vec3):
        self.pos = pos
        self.rot = rot
        self.scale = scale

class OBB:
    def __init__(self, triangles, pos : glm.vec3, rot : glm.vec3, scale : glm.vec3, collider_type=colliderTypes.normal_collider):
        """
        - triangles: List of triangles (each triangle is a list of 3 glm.vec3 vertices)
        - pos: The object's position
        - rot: The object's rotation
        - scale: The object's scale
        - collider_type: Type of collider (normal/trigger)
        """
        self.triangles = triangles
        self.transform = transform(pos, rot, scale)
        self.colliderType = collider_type

    def get_corners(self):
        """Returns all vertices from the loaded OBJ triangles in world space."""
        rotation_matrix = glm.mat3(self.transform.getModelMatrix())  # Extract rotation
        transformed_vertices = [
            self.transform.pos + rotation_matrix * (v * self.transform.scale)
            for tri in self.triangles for v in tri  # Flatten all triangle vertices
        ]
        return transformed_vertices

    def get_axes(self):
        """Returns the normal of each triangle as an axis for SAT collision checking."""
        axes = []
        for tri in self.triangles:
            edge1 = tri[1] - tri[0]
            edge2 = tri[2] - tri[0]
            normal = glm.normalize(glm.cross(edge1, edge2))
            axes.append(normal)  # Triangle face normal

        return axes

    def project_onto_axis(self, axis):
        """Projects all triangle vertices onto an axis."""
        corners = self.get_corners()
        min_proj = max_proj = glm.dot(corners[0], axis)
        for v in corners[1:]:
            projection = glm.dot(v, axis)
            min_proj = min(min_proj, projection)
            max_proj = max(max_proj, projection)

        return min_proj, max_proj

    def intersects(self, other):
        """Triangle-based OBB collision using the Separating Axis Theorem (SAT)."""
        axes = self.get_axes() + other.get_axes()

        for axis in axes:
            minA, maxA = self.project_onto_axis(axis)
            minB, maxB = other.project_onto_axis(axis)

            if maxA < minB or maxB < minA:  # Found a separating axis → no collision
                return False

        return True  # No separating axis found → collision detected
