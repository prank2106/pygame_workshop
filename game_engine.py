import pygame
import numpy as np
import math
import random

class Vector2:
    """2D vektor pro pozice a směry"""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2(0, 0)

class GameEngine:
    """Statické metody pro herní výpočty"""

    @staticmethod
    def distance(pos1, pos2):
        """Výpočet vzdálenosti mezi dvěma pozicemi"""
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def angle_between(pos1, pos2):
        """Výpočet úhlu mezi dvěma pozicemi"""
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        return math.atan2(dy, dx)

    @staticmethod
    def normalize(vector):
        """Normalizace vektoru"""
        return vector.normalize()

    @staticmethod
    def clamp(value, min_val, max_val):
        """Omezení hodnoty na daný rozsah"""
        return max(min_val, min(value, max_val))

    @staticmethod
    def lerp(start, end, t):
        """Lineární interpolace"""
        return start + (end - start) * t

    @staticmethod
    def random_position_in_circle(center, radius):
        """Náhodná pozice v kruhu"""
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        x = center.x + r * math.cos(angle)
        y = center.y + r * math.sin(angle)
        return Vector2(x, y)

    @staticmethod
    def wrap_angle(angle):
        """Zabalení úhlu do rozsahu -π až π"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    @staticmethod
    def rotate_point(point, center, angle):
        """Rotace bodu kolem středu"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        dx = point.x - center.x
        dy = point.y - center.y

        new_x = dx * cos_a - dy * sin_a + center.x
        new_y = dx * sin_a + dy * cos_a + center.y

        return Vector2(new_x, new_y)

class NumPyUtils:
    """Utility funkce využívající NumPy pro optimalizaci"""

    @staticmethod
    def generate_noise_map(width, height, scale=0.1):
        """Generování šumové mapy pro procedurální terén"""
        x = np.arange(width)
        y = np.arange(height)
        X, Y = np.meshgrid(x, y)

        # Jednoduchý Perlin-like noise
        noise = np.sin(X * scale) * np.sin(Y * scale)
        noise += 0.5 * np.sin(X * scale * 2) * np.sin(Y * scale * 2)
        noise += 0.25 * np.sin(X * scale * 4) * np.sin(Y * scale * 4)

        # Normalizace na rozsah 0-1
        noise = (noise - noise.min()) / (noise.max() - noise.min())
        return noise

    @staticmethod
    def batch_distance_calculation(positions, target_pos):
        """Hromadný výpočet vzdáleností pomocí NumPy"""
        if not positions:
            return []

        # Převedení na NumPy array
        pos_array = np.array([(pos.x, pos.y) for pos in positions])
        target_array = np.array([target_pos.x, target_pos.y])

        # Výpočet vzdáleností
        distances = np.linalg.norm(pos_array - target_array, axis=1)
        return distances.tolist()

    @staticmethod
    def filter_positions_by_distance(positions, target_pos, max_distance):
        """Filtrování pozic podle vzdálenosti"""
        distances = NumPyUtils.batch_distance_calculation(positions, target_pos)
        return [pos for pos, dist in zip(positions, distances) if dist <= max_distance]

class NPCBehavior:
    """Třída pro AI chování NPC"""

    @staticmethod
    def wander_behavior(npc, dt, wander_radius=100):
        """Základní putování NPC"""
        if not hasattr(npc, 'wander_timer'):
            npc.wander_timer = 0
        if not hasattr(npc, 'wander_target'):
            npc.wander_target = npc.position

        npc.wander_timer += dt

        if npc.wander_timer >= 3.0:  # Změna směru každé 3 sekundy
            offset_x = random.uniform(-wander_radius, wander_radius)
            offset_y = random.uniform(-wander_radius, wander_radius)
            npc.wander_target = Vector2(
                npc.position.x + offset_x,
                npc.position.y + offset_y
            )
            npc.wander_timer = 0

        # Pohyb k cíli
        direction = npc.wander_target - npc.position
        if direction.magnitude() > 2:
            direction = direction.normalize()
            npc.position = npc.position + direction * npc.speed * dt

    @staticmethod
    def flee_behavior(npc, player, dt, flee_distance=100):
        """Chování útěku od hráče"""
        direction = npc.position - player.position
        if direction.magnitude() > 0:
            direction = direction.normalize()
            npc.position = npc.position + direction * npc.speed * 1.5 * dt

    @staticmethod
    def chase_behavior(npc, player, dt):
        """Chování pronásledování hráče"""
        direction = player.position - npc.position
        if direction.magnitude() > 0:
            direction = direction.normalize()
            npc.position = npc.position + direction * npc.speed * dt

    @staticmethod
    def patrol_behavior(npc, dt, patrol_points):
        """Chování patroly mezi body"""
        if not hasattr(npc, 'patrol_index'):
            npc.patrol_index = 0
        if not hasattr(npc, 'patrol_threshold'):
            npc.patrol_threshold = 20

        if not patrol_points:
            return

        target = patrol_points[npc.patrol_index]
        distance = GameEngine.distance(npc.position, target)

        if distance < npc.patrol_threshold:
            npc.patrol_index = (npc.patrol_index + 1) % len(patrol_points)
        else:
            direction = target - npc.position
            if direction.magnitude() > 0:
                direction = direction.normalize()
                npc.position = npc.position + direction * npc.speed * dt

class Physics:
    """Fyzikální výpočty"""

    @staticmethod
    def apply_friction(velocity, friction_coefficient, dt):
        """Aplikace tření"""
        speed = velocity.magnitude()
        if speed > 0:
            friction_force = friction_coefficient * dt
            new_speed = max(0, speed - friction_force)
            return velocity.normalize() * new_speed
        return velocity

    @staticmethod
    def collision_response(obj1_pos, obj1_vel, obj2_pos, obj2_vel, obj1_mass=1, obj2_mass=1):
        """Jednoduchá kolizní odpověď"""
        # Vektor kolize
        collision_vector = obj2_pos - obj1_pos
        distance = collision_vector.magnitude()

        if distance == 0:
            return obj1_vel, obj2_vel

        collision_normal = collision_vector.normalize()

        # Relativní rychlost
        relative_velocity = obj1_vel - obj2_vel
        speed = relative_velocity.x * collision_normal.x + relative_velocity.y * collision_normal.y

        if speed < 0:
            return obj1_vel, obj2_vel

        # Impulz
        impulse = 2 * speed / (obj1_mass + obj2_mass)

        new_vel1 = Vector2(
            obj1_vel.x - impulse * obj2_mass * collision_normal.x,
            obj1_vel.y - impulse * obj2_mass * collision_normal.y
        )

        new_vel2 = Vector2(
            obj2_vel.x + impulse * obj1_mass * collision_normal.x,
            obj2_vel.y + impulse * obj1_mass * collision_normal.y
        )

        return new_vel1, new_vel2

    @staticmethod
    def is_point_in_circle(point, circle_center, radius):
        """Kontrola, zda je bod v kruhu"""
        return GameEngine.distance(point, circle_center) <= radius

    @staticmethod
    def is_point_in_rectangle(point, rect_pos, rect_width, rect_height):
        """Kontrola, zda je bod v obdélníku"""
        return (rect_pos.x <= point.x <= rect_pos.x + rect_width and
                rect_pos.y <= point.y <= rect_pos.y + rect_height)
