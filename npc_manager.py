import pygame
import random
import math
from game_engine import Vector2, GameEngine, NPCBehavior

class Goblin:
    """Třída reprezentující goblina - zloděje"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 12
        self.speed = 80
        self.state = "wandering"  # wandering, stealing, fleeing
        self.color = (139, 0, 139)  # Fialová

        # AI parametry
        self.wander_timer = 0
        self.steal_cooldown = 0
        self.flee_timer = 0
        self.catchable = True  # OPRAVA: Flag pro možnost chycení

    def update(self, dt, player):
        """Aktualizace goblina"""
        self.steal_cooldown -= dt
        self.flee_timer -= dt

        player_distance = GameEngine.distance(self.position, player.position)

        if self.state == "wandering":
            # Náhodné putování
            self.wander_timer += dt
            if self.wander_timer >= 3.0:  # Změna směru každé 3 sekundy
                offset_x = random.uniform(-80, 80)
                offset_y = random.uniform(-80, 80)
                self.target_position = Vector2(
                    self.position.x + offset_x,
                    self.position.y + offset_y
                )
                self.wander_timer = 0

            # Pokud je hráč blízko a goblin není v cooldownu, pokus o krádež
            if player_distance < 60 and self.steal_cooldown <= 0:
                self.state = "stealing"
                self.target_position = player.position

            # Pohyb k cíli
            direction = self.target_position - self.position
            if direction.magnitude() > 2:
                direction = direction.normalize()
                self.position = self.position + direction * self.speed * dt

        elif self.state == "stealing":
            # Pokus o krádež - přiblížení k hráči
            if player_distance < 25:
                # Úspěšná krádež
                if random.random() < 0.6:  # 60% šance na úspěch
                    stolen_coins = min(player.coins, random.randint(5, 15))
                    stolen_wood = min(player.wood, random.randint(0, 2))

                    player.coins -= stolen_coins
                    player.wood -= stolen_wood

                    if stolen_coins > 0 or stolen_wood > 0:
                        print(f"Goblin ti ukradl {stolen_coins} mincí a {stolen_wood} dřeva!")

                # Po krádeži útěk
                self.state = "fleeing"
                self.flee_timer = 5.0
                self.steal_cooldown = 10.0

                # Útěk od hráče
                escape_direction = self.position - player.position
                if escape_direction.magnitude() > 0:
                    escape_direction = escape_direction.normalize()
                    self.target_position = self.position + escape_direction * 200
            else:
                # Pohyb k hráči
                direction = player.position - self.position
                if direction.magnitude() > 0:
                    direction = direction.normalize()
                    self.position = self.position + direction * self.speed * dt

        elif self.state == "fleeing":
            # Útěk od hráče
            if self.flee_timer <= 0:
                self.state = "wandering"
            else:
                # Pokračování v útěku
                direction = self.target_position - self.position
                if direction.magnitude() > 2:
                    direction = direction.normalize()
                    self.position = self.position + direction * (self.speed * 1.5) * dt

    def render(self, screen, camera_x, camera_y):
        """Vykreslení goblina"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        # Barva podle stavu
        color = self.color
        if self.state == "stealing":
            color = (255, 0, 0)  # Červená při krádeži
        elif self.state == "fleeing":
            color = (255, 165, 0)  # Oranžová při útěku

        # OPRAVA: Vizuální indikátor, že je možné goblina chytit
        if self.catchable and GameEngine.distance(Vector2(screen_x, screen_y), Vector2(512, 384)) < 50:
            pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), self.size + 5, 2)

        pygame.draw.circle(screen, color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), self.size, 2)

class Leprechaun:
    """Třída reprezentující leprikóna - pomocníka"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.size = 14
        self.color = (0, 255, 0)  # Zelená
        self.teleport_timer = 0
        self.interaction_cooldown = 0

    def update(self, dt, player):
        """Aktualizace leprikóna"""
        self.teleport_timer += dt
        self.interaction_cooldown -= dt

        # Náhodná teleportace každých 15-30 sekund
        if self.teleport_timer >= random.uniform(15, 30):
            self.position.x = random.uniform(100, 900)
            self.position.y = random.uniform(100, 700)
            self.teleport_timer = 0

    def render(self, screen, camera_x, camera_y):
        """Vykreslení leprikóna"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        # Blikající efekt
        blink = int(pygame.time.get_ticks() / 500) % 2
        if blink:
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        else:
            pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), self.size)

        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), self.size, 2)

class Bear:
    """Třída reprezentující medvěda - nepřítele"""
    shared_sprite_sheet = None

    sprite_width = 64
    sprite_height = 64
    frame_count = 4
    direction_map = {
        "down": 0,
        "right": 1,
        "up": 2,
        "left": 3
    }

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 20
        self.speed = 60
        self.color = (139, 69, 19)
        self.attack_cooldown = 0
        self.wander_timer = 0
        self.frame = 0
        self.animation_timer = 0
        self.direction = "down" 
        self.current_frame = 0

    def update(self, dt, player):
        """Aktualizace medvěda"""
        self.attack_cooldown -= dt
        player_distance = GameEngine.distance(self.position, player.position)
        self.animation_timer += dt
        if self.animation_timer > 0.2:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.animation_timer = 0

        if player_distance < 100:
            direction = player.position - self.position
            if direction.magnitude() > 0:
                direction = direction.normalize()
                self.position = self.position + direction * self.speed * dt
                if abs(direction.x) > abs(direction.y):
                    self.direction = "right" if direction.x > 0 else "left"
                else:
                    self.direction = "down" if direction.y > 0 else "up"
            if player_distance < 30 and self.attack_cooldown <= 0:
                player.take_damage(15)
                self.attack_cooldown = 2.0
        else:
            self.wander_timer += dt
            if self.wander_timer >= 4.0:
                offset_x = random.uniform(-100, 100)
                offset_y = random.uniform(-100, 100)
                self.target_position = Vector2(
                    self.position.x + offset_x,
                    self.position.y + offset_y
                )
                self.wander_timer = 0
            direction = self.target_position - self.position
            if direction.magnitude() > 2:
                direction = direction.normalize()
                self.position = self.position + direction * (self.speed * 0.5) * dt
                if abs(direction.x) > abs(direction.y):
                    self.direction = "right" if direction.x > 0 else "left"
                else:
                    self.direction = "down" if direction.y > 0 else "up"

    def render(self, screen, camera_x, camera_y):
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        if Bear.shared_sprite_sheet is None:
            Bear.shared_sprite_sheet = pygame.image.load("assets/Higan.png").convert_alpha()


        row = self.direction_map[self.direction]
        col = self.frame
        frame_rect = pygame.Rect(
            col * self.sprite_width,
            row * self.sprite_height,
            self.sprite_width,
            self.sprite_height
        )
        sprite = Bear.shared_sprite_sheet.subsurface(frame_rect)
        screen.blit(sprite, (
            screen_x - self.sprite_width // 2,
            screen_y - self.sprite_height // 2
        ))

class Fox:
    """Třída reprezentující lišku - rychlého zloděje"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 10
        self.speed = 120
        self.color = (255, 165, 0)  # Oranžová
        self.steal_cooldown = 0
        self.wander_timer = 0

    def update(self, dt, player):
        """Aktualizace lišky"""
        self.steal_cooldown -= dt
        player_distance = GameEngine.distance(self.position, player.position)

        if player_distance < 50 and self.steal_cooldown <= 0:
            # Rychlá krádež mincí
            if random.random() < 0.3:  # 30% šance
                stolen_coins = min(player.coins, random.randint(1, 5))
                player.coins -= stolen_coins
                if stolen_coins > 0:
                    print(f"Liška ti ukradla {stolen_coins} mincí!")

            self.steal_cooldown = 8.0

            # Rychlý útěk
            escape_direction = self.position - player.position
            if escape_direction.magnitude() > 0:
                escape_direction = escape_direction.normalize()
                self.target_position = self.position + escape_direction * 150
        else:
            # Náhodné putování
            self.wander_timer += dt
            if self.wander_timer >= 2.0:
                offset_x = random.uniform(-60, 60)
                offset_y = random.uniform(-60, 60)
                self.target_position = Vector2(
                    self.position.x + offset_x,
                    self.position.y + offset_y
                )
                self.wander_timer = 0

        # Pohyb
        direction = self.target_position - self.position
        if direction.magnitude() > 2:
            direction = direction.normalize()
            self.position = self.position + direction * self.speed * dt

    def render(self, screen, camera_x, camera_y):
        """Vykreslení lišky"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), self.size, 2)

class Rabbit:
    """Třída reprezentující králíka - dekorativní NPC"""

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 8
        self.speed = 100
        self.color = (255, 255, 255)  # Bílá
        self.wander_timer = 0

    def update(self, dt, player):
        """Aktualizace králíka"""
        player_distance = GameEngine.distance(self.position, player.position)

        if player_distance < 40:
            # Útěk od hráče
            escape_direction = self.position - player.position
            if escape_direction.magnitude() > 0:
                escape_direction = escape_direction.normalize()
                self.target_position = self.position + escape_direction * 100
        else:
            # Náhodné putování
            self.wander_timer += dt
            if self.wander_timer >= 3.0:
                offset_x = random.uniform(-50, 50)
                offset_y = random.uniform(-50, 50)
                self.target_position = Vector2(
                    self.position.x + offset_x,
                    self.position.y + offset_y
                )
                self.wander_timer = 0

        # Pohyb
        direction = self.target_position - self.position
        if direction.magnitude() > 2:
            direction = direction.normalize()
            self.position = self.position + direction * self.speed * dt

    def render(self, screen, camera_x, camera_y):
        """Vykreslení králíka"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (screen_x, screen_y), self.size, 2)

class NPCManager:
    """Manager pro všechny NPC postavy"""

    def __init__(self, world):
        self.world = world

        # OPRAVA: Seznamy NPC jako atributy instance
        self.goblins = []
        self.leprechauns = []
        self.bears = []
        self.foxes = []
        self.rabbits = []

        # Spawn NPC
        self.spawn_npcs()

    def spawn_npcs(self):
        """Vytvoření NPC postav"""
        # Goblinové (2-3)
        for i in range(random.randint(2, 3)):
            x = random.uniform(150, 850)
            y = random.uniform(150, 650)
            self.goblins.append(Goblin(x, y))

        # Leprikónové (1-2)
        for i in range(random.randint(1, 2)):
            x = random.uniform(200, 800)
            y = random.uniform(200, 600)
            self.leprechauns.append(Leprechaun(x, y))

        # Medvědi (1-2)
        for i in range(random.randint(1, 2)):
            x = random.uniform(300, 700)
            y = random.uniform(300, 500)
            self.bears.append(Bear(x, y))

        # Lišky (2-4)
        for i in range(random.randint(2, 4)):
            x = random.uniform(100, 900)
            y = random.uniform(100, 700)
            self.foxes.append(Fox(x, y))

        # Králíci (3-6)
        for i in range(random.randint(3, 6)):
            x = random.uniform(150, 850)
            y = random.uniform(150, 650)
            self.rabbits.append(Rabbit(x, y))

    def update(self, dt, player):
        """Aktualizace všech NPC"""
        # Aktualizace goblinů
        for goblin in self.goblins[:]:  # Kopie seznamu pro bezpečné mazání
            goblin.update(dt, player)

        # Aktualizace leprikónů
        for leprechaun in self.leprechauns:
            leprechaun.update(dt, player)

        # Aktualizace medvědů
        for bear in self.bears:
            bear.update(dt, player)

        # Aktualizace lišek
        for fox in self.foxes:
            fox.update(dt, player)

        # Aktualizace králíků
        for rabbit in self.rabbits:
            rabbit.update(dt, player)

    def render(self, screen, camera_x, camera_y):
        """Vykreslení všech NPC"""
        # Vykreslení goblinů
        for goblin in self.goblins:
            goblin.render(screen, camera_x, camera_y)

        # Vykreslení leprikónů
        for leprechaun in self.leprechauns:
            leprechaun.render(screen, camera_x, camera_y)

        # Vykreslení medvědů
        for bear in self.bears:
            bear.render(screen, camera_x, camera_y)

        # Vykreslení lišek
        for fox in self.foxes:
            fox.render(screen, camera_x, camera_y)

        # Vykreslení králíků
        for rabbit in self.rabbits:
            rabbit.render(screen, camera_x, camera_y)
