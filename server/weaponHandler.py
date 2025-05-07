from server.hitbox import hitbox
import time, math

class Weapon:
    def __init__(self, weapon_data:dict):
        self.weapon_model = weapon_data["weaponmodel"]

class Gun(Weapon):
    def __init__(self, weapon_data):
        super().__init__(weapon_data)

        self.weapon_firerate = weapon_data["fire_rate"]
        self.weapon_firerate = weapon_data["max_ammo"]
        self.weapon_firerate = weapon_data["reload_time"]

        self.hitscan = weapon_data["hitscan"]

        if self.hitscan:
            self.max_range = weapon_data["max_range"]

        self.ticker = time.time()
        self.ticker_mod = time.time()

    def try_fire(self, holder_pos:tuple):
        if self.ticker-self.ticker_mod >= self.weapon_firerate:
            self.ticker_mod = self.ticker
            if self.hitscan:
                self.fire_hitscan(holder_pos)

    def fire_hitscan(self, holder_pos:tuple, player_hitboxes:list[hitbox]):
        ox, oy, oz, rot_x, rot_y = holder_pos

        rot_x = math.radians(rot_x)
        rot_y = math.radians(rot_y)   

        def check_col(hit:hitbox):
            if hit.get_colliding(x_pos, y_pos, z_pos):
                return True

            return False         

        for mod in range(0, self.max_range, 0.01):
            x_pos = mod(math.cos(rot_x)*math.sin(rot_y))+ox
            y_pos = mod(math.sin(rot_y))+oy
            z_pos = mod(math.sin(rot_y)*math.sin(rot_x))+oz

            hit = list(map(check_col, player_hitboxes))

            if True in hit:
                idx = hit.index(True)
                player_hitboxes[idx].hit_owner
