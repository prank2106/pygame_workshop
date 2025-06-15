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
            self.image = pygame.image.load("assets/tree_small.png").convert_alpha()
        else:  # big tree
            self.image = pygame.image.load("assets/tree_big.png").convert_alpha()

        
        self.dying = False
        self.death_timer = 0.0

        self.rect = self.image.get_rect(center=(x, y))
        self.max_health = 25 if tree_type == "small" else 75
        self.health = self.max_health
        self.sway_offset = random.uniform(0, 2 * math.pi)  # Pro animaci kývání

    def update(self, dt):
        """Aktualizace stromu (animace pokácení)"""
        
        if self.dying:
            self.death_timer -= dt


    def render(self, screen, camera_x, camera_y):
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)
        # Vytvoříme kopii obrázku pro úpravu průhlednosti
        image = self.image.copy()

        if self.dying:
            # Vypočítáme poměr zbývajícího času
            ratio = max(0, self.death_timer / 0.4)  # 0.4 je výchozí doba zániku
            alpha = int(255 * ratio)
            image.set_alpha(alpha)

        screen.blit(image, image.get_rect(center=(screen_x, screen_y)))



class Bush:
    """Třída reprezentující keř - dekorativní objekt"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.image = pygame.image.load("assets/bush.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

    def render(self, screen, camera_x, camera_y):
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)
        screen.blit(self.image, self.image.get_rect(center=(screen_x, screen_y)))

class Rock:
    """Třída reprezentující kámen - překážka"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.image = pygame.image.load("assets/rock.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = max(self.rect.width, self.rect.height) // 2


    def render(self, screen, camera_x, camera_y):
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)
        screen.blit(self.image, self.image.get_rect(center=(screen_x, screen_y)))

class Decoration:
    def __init__(self, x, y, image):
        self.position = Vector2(x, y)
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def render(self, screen, camera_x, camera_y):
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)
        screen.blit(self.image, self.image.get_rect(center=(screen_x, screen_y)))


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
        self.decorations = []
        self.decoration_images = [
            pygame.image.load("assets/props_grass_01.png").convert_alpha(),
            pygame.image.load("assets/props_grass_02.png").convert_alpha(),
            pygame.image.load("assets/props_grass_08.png").convert_alpha(),
            pygame.image.load("assets/props_grass_07.png").convert_alpha(),
            pygame.image.load("assets/props_vegetation_18.png").convert_alpha(),
            pygame.image.load("assets/props_vegetation_19.png").convert_alpha(),
            pygame.image.load("assets/props_vegetation_23.png").convert_alpha(),
            pygame.image.load("assets/props_vegetation_26.png").convert_alpha(),
        ]
    
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

        # Generování dekoraci
        self.generate_decorations()

        print(f"Vygenerováno: {len(self.trees)} stromů, {len(self.bushes)} keřů, {len(self.rocks)} kamenů, {len(self.decorations)} dekorací")

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
        num_bushes = random.randint(50, 100)

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
    def generate_decorations(self):
        num = random.randint(300, 400)
        for _ in range(num):
            x = random.uniform(0, self.world_width)
            y = random.uniform(0, self.world_height)
            if self.is_position_clear(x, y, 20):
                image = random.choice(self.decoration_images)
                self.decorations.append(Decoration(x, y, image))

    def is_position_walkable(self, x, y, radius=12):
        """Zda je možné na dané pozici stát (bez kolize s pevnými objekty)"""
        pos = Vector2(x, y)

        for tree in self.trees:
            if tree.dying:
                continue  # Nebereme v úvahu umírající stromy
            tree_radius = tree.image.get_width() // 2
            if GameEngine.distance(pos, tree.position) < radius + tree_radius:
                return False

        for rock in self.rocks:
            if GameEngine.distance(pos, rock.position) < radius + rock.radius:
                return False

        return True

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
            tree_radius = tree.image.get_width() // 2
            if GameEngine.distance(pos, tree.position) < radius + tree_radius:
                return False

        # Kontrola s kameny
        for rock in self.rocks:
            rock_radius = rock.image.get_width() // 2
            if GameEngine.distance(pos, rock.position) < radius + rock.radius:
                return False

        return True

    def update(self, dt):
        """Aktualizace herního světa"""
        # Aktualizace stromů
        for tree in self.trees[:]:  # kopie seznamu, protože můžeme mazat
            tree.update(dt)
            if tree.dying and tree.death_timer <= 0:
                self.trees.remove(tree)

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
        screen.fill((34, 139, 34))

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
        
        for deco in self.decorations:
            if (camera_x - 50 <= deco.position.x <= camera_x + self.screen_width + 50 and
                camera_y - 50 <= deco.position.y <= camera_y + self.screen_height + 50):
                deco.render(screen, camera_x, camera_y)

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
