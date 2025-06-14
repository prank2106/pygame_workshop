import pygame
import random
import math
from game_engine import Vector2, GameEngine, NumPyUtils

class Tree:
    """Třída reprezentující strom"""

    def __init__(self, x, y, tree_type="small"):
        self.position = Vector2(x, y)
        self.tree_type = tree_type  # "small" nebo "big"

        if tree_type == "small":
            self.size = random.randint(15, 25)
            self.max_health = 25
            self.color = (34, 139, 34)
        else:  # big tree
            self.size = random.randint(30, 45)
            self.max_health = 75
            self.color = (0, 100, 0)

        self.health = self.max_health
        self.sway_offset = random.uniform(0, 2 * math.pi)  # Pro animaci kývání

    def update(self, dt):
        """Aktualizace stromu (animace kývání)"""
        pass

    def render(self, screen, camera_x, camera_y):
        """Vykreslení stromu"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        # Jemné kývání stromu
        sway = math.sin(pygame.time.get_ticks() * 0.002 + self.sway_offset) * 2

        # Kmen stromu
        trunk_color = (139, 69, 19)
        trunk_width = max(4, self.size // 8)
        trunk_height = self.size // 2

        pygame.draw.rect(screen, trunk_color, 
                        (screen_x - trunk_width//2 + int(sway), 
                         screen_y + self.size//2, 
                         trunk_width, 
                         trunk_height))

        # Koruna stromu (s indikátorem poškození)
        if self.health < self.max_health:
            # Světlejší barva při poškození
            damage_ratio = 1 - (self.health / self.max_health)
            r = int(self.color[0] + (139 - self.color[0]) * damage_ratio)
            g = int(self.color[1] * (1 - damage_ratio * 0.5))
            b = int(self.color[2] * (1 - damage_ratio * 0.5))
            crown_color = (r, g, b)
        else:
            crown_color = self.color

        pygame.draw.circle(screen, crown_color, 
                          (screen_x + int(sway), screen_y), self.size)
        pygame.draw.circle(screen, (0, 100, 0), 
                          (screen_x + int(sway), screen_y), self.size, 2)

class Bush:
    """Třída reprezentující keř - dekorativní objekt"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.size = random.randint(8, 15)
        self.color = (0, 128, 0)

    def render(self, screen, camera_x, camera_y):
        """Vykreslení keře"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (0, 80, 0), (screen_x, screen_y), self.size, 1)

class Rock:
    """Třída reprezentující kámen - překážka"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.size = random.randint(12, 20)
        self.color = (128, 128, 128)

    def render(self, screen, camera_x, camera_y):
        """Vykreslení kamene"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (64, 64, 64), (screen_x, screen_y), self.size, 2)

class World:
    """Třída pro správu herního světa"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Rozměry světa (větší než obrazovka)
        self.world_width = screen_width * 2
        self.world_height = screen_height * 2

        # Seznamy objektů ve světě
        self.trees = []
        self.bushes = []
        self.rocks = []

        # Generování světa
        self.generate_world()

    def generate_world(self):
        """Procedurální generování herního světa"""
        print("Generování herního světa...")

        # Generování šumové mapy pro hustotu vegetace
        noise_map = NumPyUtils.generate_noise_map(
            self.world_width // 20, 
            self.world_height // 20, 
            scale=0.1
        )

        # Generování stromů
        self.generate_trees(noise_map)

        # Generování keřů
        self.generate_bushes()

        # Generování kamenů
        self.generate_rocks()

        print(f"Vygenerováno: {len(self.trees)} stromů, {len(self.bushes)} keřů, {len(self.rocks)} kamenů")

    def generate_trees(self, noise_map):
        """Generování stromů na základě šumové mapy"""
        num_trees = random.randint(150, 250)

        for _ in range(num_trees):
            x = random.uniform(50, self.world_width - 50)
            y = random.uniform(50, self.world_height - 50)

            # Kontrola šumové mapy pro hustotu vegetace
            noise_x = int((x / self.world_width) * noise_map.shape[1])
            noise_y = int((y / self.world_height) * noise_map.shape[0])
            noise_x = max(0, min(noise_map.shape[1] - 1, noise_x))
            noise_y = max(0, min(noise_map.shape[0] - 1, noise_y))

            vegetation_density = noise_map[noise_y, noise_x]

            # Více stromů v oblastech s vyšší hustotou vegetace
            if random.random() < vegetation_density * 0.8:
                # Určení typu stromu na základě hustoty
                if vegetation_density > 0.6 and random.random() < 0.3:
                    tree_type = "big"
                else:
                    tree_type = "small"

                # Kontrola kolize s existujícími stromy
                too_close = False
                for existing_tree in self.trees:
                    if GameEngine.distance(Vector2(x, y), existing_tree.position) < 40:
                        too_close = True
                        break

                if not too_close:
                    self.trees.append(Tree(x, y, tree_type))

    def generate_bushes(self):
        """Generování keřů"""
        num_bushes = random.randint(80, 120)

        for _ in range(num_bushes):
            x = random.uniform(30, self.world_width - 30)
            y = random.uniform(30, self.world_height - 30)

            # Kontrola kolize s stromy
            too_close = False
            for tree in self.trees:
                if GameEngine.distance(Vector2(x, y), tree.position) < 35:
                    too_close = True
                    break

            if not too_close:
                self.bushes.append(Bush(x, y))

    def generate_rocks(self):
        """Generování kamenů"""
        num_rocks = random.randint(30, 50)

        for _ in range(num_rocks):
            x = random.uniform(40, self.world_width - 40)
            y = random.uniform(40, self.world_height - 40)

            # Kontrola kolize s ostatními objekty
            too_close = False

            # Kontrola se stromy
            for tree in self.trees:
                if GameEngine.distance(Vector2(x, y), tree.position) < 45:
                    too_close = True
                    break

            # Kontrola s keři
            if not too_close:
                for bush in self.bushes:
                    if GameEngine.distance(Vector2(x, y), bush.position) < 25:
                        too_close = True
                        break

            if not too_close:
                self.rocks.append(Rock(x, y))

    def get_objects_in_area(self, center_x, center_y, radius):
        """Získání objektů v dané oblasti"""
        center_pos = Vector2(center_x, center_y)
        objects_in_area = []

        # Stromy
        for tree in self.trees:
            if GameEngine.distance(tree.position, center_pos) <= radius:
                objects_in_area.append(('tree', tree))

        # Keře
        for bush in self.bushes:
            if GameEngine.distance(bush.position, center_pos) <= radius:
                objects_in_area.append(('bush', bush))

        # Kameny
        for rock in self.rocks:
            if GameEngine.distance(rock.position, center_pos) <= radius:
                objects_in_area.append(('rock', rock))

        return objects_in_area

    def is_position_clear(self, x, y, radius=20):
        """Kontrola, zda je pozice volná"""
        pos = Vector2(x, y)

        # Kontrola se stromy
        for tree in self.trees:
            if GameEngine.distance(pos, tree.position) < radius + tree.size:
                return False

        # Kontrola s kameny
        for rock in self.rocks:
            if GameEngine.distance(pos, rock.position) < radius + rock.size:
                return False

        return True

    def update(self, dt):
        """Aktualizace herního světa"""
        # Aktualizace stromů
        for tree in self.trees:
            tree.update(dt)

        # Možné regenerování stromů
        if random.random() < 0.001:  # 0.1% šance každý frame
            self.try_regrow_tree()

    def try_regrow_tree(self):
        """Pokus o znovu vyrostnutí stromu"""
        if len(self.trees) < 100:  # Pouze pokud je méně než 100 stromů
            x = random.uniform(50, self.world_width - 50)
            y = random.uniform(50, self.world_height - 50)

            if self.is_position_clear(x, y, 40):
                tree_type = "small" if random.random() < 0.8 else "big"
                self.trees.append(Tree(x, y, tree_type))

    def render(self, screen, camera_x, camera_y):
        """Vykreslení herního světa"""
        # Vykreslení pozadí
        screen.fill((34, 139, 34))  # Lesní zelená

        # Culling - vykreslení pouze objektů na obrazovce
        screen_rect = pygame.Rect(camera_x - 50, camera_y - 50, 
                                  self.screen_width + 100, 
                                  self.screen_height + 100)

        # Vykreslení keřů (v pozadí)
        for bush in self.bushes:
            if (camera_x - 50 <= bush.position.x <= camera_x + self.screen_width + 50 and
                camera_y - 50 <= bush.position.y <= camera_y + self.screen_height + 50):
                bush.render(screen, camera_x, camera_y)

        # Vykreslení kamenů
        for rock in self.rocks:
            if (camera_x - 50 <= rock.position.x <= camera_x + self.screen_width + 50 and
                camera_y - 50 <= rock.position.y <= camera_y + self.screen_height + 50):
                rock.render(screen, camera_x, camera_y)

        # Vykreslení stromů (v popředí)
        for tree in self.trees:
            if (camera_x - 50 <= tree.position.x <= camera_x + self.screen_width + 50 and
                camera_y - 50 <= tree.position.y <= camera_y + self.screen_height + 50):
                tree.render(screen, camera_x, camera_y)

    def get_minimap_data(self, camera_x, camera_y, minimap_size):
        """Získání dat pro minimapu"""
        minimap_data = {
            'trees': [],
            'bushes': [],
            'rocks': []
        }

        # Měřítko minimapy
        scale_x = minimap_size / self.world_width
        scale_y = minimap_size / self.world_height

        # Převedení pozic stromů
        for tree in self.trees:
            minimap_x = int(tree.position.x * scale_x)
            minimap_y = int(tree.position.y * scale_y)
            minimap_data['trees'].append((minimap_x, minimap_y, tree.tree_type))

        # Převedení pozic keřů
        for bush in self.bushes:
            minimap_x = int(bush.position.x * scale_x)
            minimap_y = int(bush.position.y * scale_y)
            minimap_data['bushes'].append((minimap_x, minimap_y))

        # Převedení pozic kamenů
        for rock in self.rocks:
            minimap_x = int(rock.position.x * scale_x)
            minimap_y = int(rock.position.y * scale_y)
            minimap_data['rocks'].append((minimap_x, minimap_y))

        return minimap_data
