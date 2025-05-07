class hitbox:
    def __init__(self, server):
        self.hit_owner = 0

        self.min_x = 0
        self.min_y = 0
        self.min_z = 0

        self.max_x = 1
        self.max_y = 2
        self.max_z = 1

    def move(self, pos:list):
        self.min_x = pos[0]
        self.min_y = pos[1]
        self.min_z = pos[2]

        self.max_x = pos[0] + 1
        self.max_y = pos[1] + 2
        self.max_z = pos[2] + 1

    def get_colliding(self, x:float, y:float, z:float):
        if self.min_x < x < self.max_x:
            if self.min_y < y < self.max_y:
                if self.min_z < z < self.max_z:
                    return True
                
        return False