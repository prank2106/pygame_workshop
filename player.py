import pygame
import math
import random
from game_engine import Vector2, GameEngine

class Player:
    """Třída reprezentující hráče - dřevorubce"""

    def __init__(self, start_x, start_y):
        self.position = Vector2(start_x, start_y)
        self.velocity = Vector2(0, 0)
        self.size = 15

        self.sprite_sheet = pygame.image.load("assets/lumberjack_sheet_9x3.png").convert_alpha()
        self.frame_width = self.sprite_sheet.get_width() // 9
        self.frame_height = self.sprite_sheet.get_height() // 3
        self.animation_timer = 0
        self.animation_index = 0


        # Herní statistiky
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        self.coins = 0
        self.wood = 0

        # Inventář
        self.food_count = 1  # Počáteční jídlo
        self.potion_count = 0
        self.has_better_axe = False
        self.has_protection = False

        # Pohybové parametry
        self.speed = 150  # pixelů za sekundu
        self.base_speed = 150

        # Animace a vizuální efekty
        self.chopping_animation = 0
        self.damage_flash = 0
        self.last_direction = Vector2(0, -1)  # Poslední směr pohybu

        # Časovače
        self.energy_regen_timer = 0
        self.protection_timer = 0
        self.catch_cooldown = 0  # OPRAVA: Cooldown pro chytání goblina

    def get_current_frame(self):
        if self.last_direction.y > 0:
            row = 0  # dolů
        elif self.last_direction.x > 0:
            row = 1  # doprava
        elif self.last_direction.x < 0:
            row = 1  # LEVÁ = použij doprava a zrcadli
        elif self.last_direction.y < 0:
            row = 2  # nahoru
        else:
            row = 0

        col = self.animation_index % 9
        frame_rect = pygame.Rect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
        frame = self.sprite_sheet.subsurface(frame_rect)

        # Zrcadlení doleva
        if self.last_direction.x < 0:
            frame = pygame.transform.flip(frame, True, False)

        return frame


    def handle_input(self, keys):
        """Zpracování vstupu od hráče"""
        movement = Vector2(0, 0)

        if keys[pygame.K_LEFT]:
            movement.x -= 1
            self.last_direction = Vector2(-1, 0)
        if keys[pygame.K_RIGHT]:
            movement.x += 1
            self.last_direction = Vector2(1, 0)
        if keys[pygame.K_UP]:
            movement.y -= 1
            self.last_direction = Vector2(0, -1)
        if keys[pygame.K_DOWN]:
            movement.y += 1
            self.last_direction = Vector2(0, 1)

        # Normalizace diagonálního pohybu
        if movement.magnitude() > 0:
            movement = movement.normalize()

        # OPRAVA: Aplikace rychlosti podle lepší sekery
        current_speed = self.speed
        if self.has_better_axe:
            current_speed = self.base_speed * 1.3  # 30% rychlejší pohyb

        self.velocity = movement * current_speed

    def update(self, dt):
        """Aktualizace hráče"""
        # Pohyb
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt

        # Regenerace energie
        self.energy_regen_timer += dt
        if self.energy_regen_timer >= 2.0:  # Každé 2 sekundy
            self.energy = min(self.max_energy, self.energy + 5)
            self.energy_regen_timer = 0

        # Snížení animačních časovačů
        if self.chopping_animation > 0:
            self.chopping_animation -= dt
        if self.damage_flash > 0:
            self.damage_flash -= dt

        # Snížení cooldownů
        if self.catch_cooldown > 0:
            self.catch_cooldown -= dt

        # Časovač ochrany
        if self.protection_timer > 0:
            self.protection_timer -= dt
            if self.protection_timer <= 0:
                self.has_protection = False
        
        # Animace chůze
        if self.velocity.magnitude() > 0:
            self.animation_timer += dt
            if self.animation_timer > 0.1:  # každých 0.1s další frame
                self.animation_index = (self.animation_index + 1) % 9
                self.animation_timer = 0
        else:
            self.animation_index = 0  # reset na první snímek při stání


    def try_chop_tree(self, trees):
        """Pokus o pokácení stromu"""
        if self.energy < 10:
            return False  # Nedostatek energie

        # Najít nejbližší strom
        closest_tree = None
        closest_distance = float('inf')

        for tree in trees:
            distance = GameEngine.distance(self.position, tree.position)
            if distance < 40 and distance < closest_distance:  # V dosahu
                closest_tree = tree
                closest_distance = distance

        if closest_tree:
            # OPRAVA: Aplikace efektu lepší sekery
            if self.has_better_axe:
                damage = 35  # Více poškození s lepší sekerou
                self.energy -= 8  # Méně energie se spotřebuje
            else:
                damage = 25  # Standardní poškození
                self.energy -= 10  # Standardní spotřeba energie

            closest_tree.health -= damage
            self.chopping_animation = 0.5  # Animace sekání

            # Pokácení stromu
            if closest_tree.health <= 0:
                # Odměna podle typu stromu
                if closest_tree.tree_type == "small":
                    wood_gained = random.randint(1, 3)
                else:  # big tree
                    wood_gained = 5

                self.wood += wood_gained
                trees.remove(closest_tree)
                return True

        return False

    def try_catch_goblin(self, goblins):
        """OPRAVA: Pokus o chytání goblina"""
        if self.catch_cooldown > 0:
            return False  # Ještě je cooldown

        # Najít nejbližšího goblina
        closest_goblin = None
        closest_distance = float('inf')

        for goblin in goblins:
            distance = GameEngine.distance(self.position, goblin.position)
            if distance < 50 and distance < closest_distance:  # V dosahu chytání
                closest_goblin = goblin
                closest_distance = distance

        if closest_goblin:
            # Šance na chycení
            catch_chance = 0.7  # 70% šance na úspěch
            if self.has_better_axe:
                catch_chance = 0.85  # Lepší sekera pomáhá i při chytání

            if random.random() < catch_chance:
                # Úspěšné chycení
                reward_coins = random.randint(15, 30)
                reward_wood = random.randint(0, 2)

                self.coins += reward_coins
                self.wood += reward_wood

                # Odebrání goblina ze seznamu
                goblins.remove(closest_goblin)
                self.catch_cooldown = 3.0  # 3 sekundy cooldown

                print(f"Chytil jsi goblina! Získal jsi {reward_coins} mincí a {reward_wood} dřeva!")
                return True
            else:
                # Neúspěšné chycení
                self.catch_cooldown = 1.0  # Kratší cooldown při neúspěchu
                print("Goblin ti utekl!")
                return False

        return False

    def interact_with_leprechaun(self, leprechauns):
        """Interakce s leprikónem"""
        closest_leprechaun = None
        closest_distance = float('inf')

        for leprechaun in leprechauns:
            distance = GameEngine.distance(self.position, leprechaun.position)
            if distance < 50 and distance < closest_distance:
                closest_leprechaun = leprechaun
                closest_distance = distance

        if closest_leprechaun and closest_leprechaun.interaction_cooldown <= 0:
            reward_type = random.choice(['coins', 'wood', 'health', 'teleport'])

            if reward_type == 'coins':
                reward = random.randint(20, 50)
                self.coins += reward
                print(f"Leprikón ti dal {reward} mincí!")
            elif reward_type == 'wood':
                reward = random.randint(3, 8)
                self.wood += reward
                print(f"Leprikón ti dal {reward} dřeva!")
            elif reward_type == 'health':
                self.health = min(self.max_health, self.health + 30)
                print("Leprikón tě vyléčil!")
            elif reward_type == 'teleport':
                # Teleportace na náhodné místo
                self.position.x = random.randint(100, 800)
                self.position.y = random.randint(100, 600)
                print("Leprikón tě teleportoval!")

            closest_leprechaun.interaction_cooldown = 10.0  # 10 sekund cooldown
            return True

        return False

    def use_food(self):
        """Použití jídla pro doplnění energie"""
        if self.food_count > 0 and self.energy < self.max_energy:
            self.food_count -= 1
            self.energy = min(self.max_energy, self.energy + 40)
            print("Použil jsi jídlo! Energie doplněna.")
            return True
        return False

    def use_potion(self):
        """Použití lektvaru pro doplnění zdraví"""
        if self.potion_count > 0 and self.health < self.max_health:
            self.potion_count -= 1
            self.health = min(self.max_health, self.health + 50)
            print("Použil jsi lektvar! Zdraví doplněno.")
            return True
        return False

    def take_damage(self, damage):
        """Způsobení poškození hráči"""
        if self.has_protection:
            damage = damage // 2  # Ochrana snižuje poškození na polovinu

        self.health -= damage
        self.damage_flash = 0.3  # Flash efekt při poškození

        if self.health <= 0:
            self.health = 0

    def add_item(self, item_type, amount=1):
        """OPRAVA: Přidání předmětu do inventáře"""
        if item_type == "food":
            self.food_count += amount
        elif item_type == "potion":
            self.potion_count += amount
        elif item_type == "better_axe":
            self.has_better_axe = True
            self.speed = self.base_speed * 1.3  # Rychlejší pohyb
            print("Získal jsi lepší sekeru! Rychlejší kácení a pohyb.")
        elif item_type == "protection":
            self.has_protection = True
            self.protection_timer = 60.0  # 60 sekund ochrany
            print("Získal jsi ochranu! Poloviční poškození na 60 sekund.")

    def render(self, screen, camera_x, camera_y):
        """Vykreslení hráče"""
        screen_x = int(self.position.x - camera_x - self.frame_width // 2)
        screen_y = int(self.position.y - camera_y - self.frame_height // 2)

        frame = self.get_current_frame()
        screen.blit(frame, (screen_x, screen_y))

        # Barva hráče (červená při poškození)
        color = (255, 100, 100) if self.damage_flash > 0 else (0, 0, 255)

        # Efekt ochrany (blikání)
        if self.has_protection:
            blink = int(pygame.time.get_ticks() / 200) % 2
            if blink:
                color = (255, 255, 0)  # Žlutá barva při ochraně

        if self.chopping_animation > 0:
            # Vykreslení sekery
            axe_x = screen_x + int(self.last_direction.x * 25)
            axe_y = screen_y + int(self.last_direction.y * 25)

            axe_color = (200, 100, 50) if not self.has_better_axe else (150, 75, 0)
            pygame.draw.line(screen, axe_color, (screen_x, screen_y), (axe_x, axe_y), 4)
            pygame.draw.circle(screen, (100, 50, 0), (axe_x, axe_y), 8)
