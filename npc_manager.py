import pygame
import random
import math
from game_engine import Vector2, GameEngine, NPCBehavior

class Goblin:
    """Třída reprezentující goblina - zloděje"""

    shared_sprite_sheet = None

    sprite_width = 48
    sprite_height = 48
    frame_count = 3  # assuming 3 frames per row
    animation_speed = 0.15  # seconds per frame

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 12
        self.speed = 80
        self.state = "wandering"  # wandering, stealing, fleeing
        self.color = (139, 0, 139)  # Fialová

        # AI parameters
        self.wander_timer = 0
        self.steal_cooldown = 0
        self.flee_timer = 0
        self.catchable = True  # Flag for catchability

        # Animation
        self.animation_timer = 0
        self.frame = 0

    def update(self, dt, player, world):
        """Aktualizace goblina"""
        self.steal_cooldown -= dt
        self.flee_timer -= dt

        player_distance = GameEngine.distance(self.position, player.position)

        self.animation_timer += dt
        if self.animation_timer > self.animation_speed:
            self.frame = (self.frame + 1) % self.frame_count
            self.animation_timer = 0

        if self.state == "wandering":
            # Random wandering
            self.wander_timer += dt
            if self.wander_timer >= 3.0:  # Change direction every 3 seconds
                offset_x = random.uniform(-80, 80)
                offset_y = random.uniform(-80, 80)
                self.target_position = Vector2(
                    self.position.x + offset_x,
                    self.position.y + offset_y
                )
                self.wander_timer = 0

            # Attempt to steal if player nearby and cooldown done
            if player_distance < 60 and self.steal_cooldown <= 0:
                self.state = "stealing"
                self.target_position = player.position

            # Move toward target
            direction = self.target_position - self.position
            if direction.magnitude() > 2:
                direction = direction.normalize()
                new_pos = self.position + direction * self.speed * dt
                if not world.is_inside_fence(new_pos.x, new_pos.y, self.size):
                    self.position = new_pos


        elif self.state == "stealing":
            # Move toward player to steal
            if player_distance < 25:
                # Successful steal chance
                if random.random() < 0.6:
                    stolen_coins = min(player.coins, random.randint(5, 15))
                    stolen_wood = min(player.wood, random.randint(0, 2))

                    player.coins -= stolen_coins
                    player.wood -= stolen_wood

                    if stolen_coins > 0 or stolen_wood > 0:
                        print(f"Goblin ti ukradl {stolen_coins} mincí a {stolen_wood} dřeva!")

                # After stealing, flee
                self.state = "fleeing"
                self.flee_timer = 5.0
                self.steal_cooldown = 10.0

                escape_direction = self.position - player.position
                if escape_direction.magnitude() > 0:
                    escape_direction = escape_direction.normalize()
                    self.target_position = self.position + escape_direction * 200
            else:
                # Move closer to player
                direction = player.position - self.position
                if direction.magnitude() > 0:
                    direction = direction.normalize()
                    self.position = self.position + direction * self.speed * dt

        elif self.state == "fleeing":
            # Flee from player
            if self.flee_timer <= 0:
                self.state = "wandering"
            else:
                direction = self.target_position - self.position
                if direction.magnitude() > 2:
                    direction = direction.normalize()
                    self.position = self.position + direction * (self.speed * 1.5) * dt

    def render(self, screen, camera_x, camera_y):
        """Vykreslení goblina podle směru pohybu"""

        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        if Goblin.shared_sprite_sheet is None:
            Goblin.shared_sprite_sheet = pygame.image.load("assets/goblin_sprite_sheet.png").convert_alpha()

        # Movement direction vector
        move_dir = self.target_position - self.position
        if move_dir.magnitude() > 2:
            move_dir = move_dir.normalize()
        else:
            move_dir = Vector2(0, 0)  # idle

        # Determine animation row based on direction
        if move_dir.magnitude() == 0:
            anim_row = 0  # idle/down row
            frame = 0
        else:
            abs_x = abs(move_dir.x)
            abs_y = abs(move_dir.y)
            if abs_x > abs_y:
                anim_row = 1 if move_dir.x < 0 else 2  # left or right
            else:
                anim_row = 3 if move_dir.y < 0 else 0  # up or down

            frame = self.frame

        frame_rect = pygame.Rect(
            frame * self.sprite_width,
            anim_row * self.sprite_height,
            self.sprite_width,
            self.sprite_height
        )

        sprite = Goblin.shared_sprite_sheet.subsurface(frame_rect)

        scaled_sprite = pygame.transform.smoothscale(
            sprite,
            (self.sprite_width // 2, self.sprite_height // 2)
        )

        # Optional colored overlay based on state
        overlay_color = None
        if self.state == "stealing":
            overlay_color = (255, 0, 0, 100)  # translucent red
        elif self.state == "fleeing":
            overlay_color = (255, 165, 0, 100)  # translucent orange

        if overlay_color:
            overlay_surf = pygame.Surface((self.sprite_width // 2, self.sprite_height // 2), pygame.SRCALPHA)
            overlay_surf.fill(overlay_color)
            scaled_sprite.blit(overlay_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Catchable indicator
        if self.catchable and GameEngine.distance(Vector2(screen_x, screen_y), Vector2(512, 384)) < 50:
            pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), self.size + 5, 2)

        screen.blit(scaled_sprite, (
            screen_x - (self.sprite_width // 4),
            screen_y - (self.sprite_height // 4)
        ))


class Leprechaun:
    """Třída reprezentující leprikóna - pomocníka"""

    static_image = None

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.size = 14
        self.teleport_timer = 0
        self.interaction_cooldown = 0

    def update(self, dt, player, world):
        """Aktualizace leprikóna"""
        self.teleport_timer += dt
        self.interaction_cooldown -= dt

        # Náhodná teleportace každých 15–30 sekund
        if self.teleport_timer >= random.uniform(15, 30):
            self.position.x = random.uniform(100, 900)
            self.position.y = random.uniform(100, 700)
            self.teleport_timer = 0

    def render(self, screen, camera_x, camera_y):
        """Vykreslení leprikóna"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        if Leprechaun.static_image is None:
            Leprechaun.static_image = pygame.image.load("assets/leprechaun_static.png").convert_alpha()

        sprite = Leprechaun.static_image

        # Zvětšení statického obrázku
        scale_factor = 0.6
        scaled_sprite = pygame.transform.smoothscale(
            sprite,
            (int(sprite.get_width() * scale_factor), int(sprite.get_height() * scale_factor))
        )

        screen.blit(scaled_sprite, (
            screen_x - scaled_sprite.get_width() // 2,
            screen_y - scaled_sprite.get_height() // 2
        ))


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

    def update(self, dt, player, world):
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
                new_pos = self.position + direction * self.speed * dt
                if not world.is_inside_fence(new_pos.x, new_pos.y, self.size):
                    self.position = new_pos
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

    shared_sprite_sheet = None

    sprite_width = 60
    sprite_height = 48
    frame_count = 3
    animation_row = 6.6

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 10
        self.speed = 120
        self.color = (255, 165, 0)  # Oranžová
        self.steal_cooldown = 0
        self.wander_timer = 0
        self.animation_timer = 0
        self.frame = 0
        self.last_direction_x = -1  # Facing left initially

    def update(self, dt, player, world):
        """Aktualizace lišky"""
        self.steal_cooldown -= dt
        self.animation_timer += dt

        if self.animation_timer > 0.15:
            self.frame = (self.frame + 1) % self.frame_count
            self.animation_timer = 0

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
            new_pos = self.position + direction * self.speed * dt
            if not world.is_inside_fence(new_pos.x, new_pos.y, self.size):
                self.position = new_pos

            # Update facing direction
            if abs(direction.x) > 0.1:
                self.last_direction_x = 1 if direction.x > 0 else -1

    def render(self, screen, camera_x, camera_y):
        """Vykreslení lišky pomocí sprite sheetu"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        if Fox.shared_sprite_sheet is None:
            Fox.shared_sprite_sheet = pygame.image.load("assets/fox_sprite_sheet.png").convert_alpha()

        is_moving = (self.target_position - self.position).magnitude() > 2

        if is_moving:
            y_offset = int(self.sprite_height * self.animation_row)
            frame = self.frame
        else:
            y_offset = 0
            frame = 0

        frame_rect = pygame.Rect(
            frame * self.sprite_width,
            y_offset,
            self.sprite_width,
            self.sprite_height
        )

        sprite = Fox.shared_sprite_sheet.subsurface(frame_rect)

        # Flip if facing right
        if self.last_direction_x > 0:
            sprite = pygame.transform.flip(sprite, True, False)

        # Scale down
        scaled_sprite = pygame.transform.smoothscale(
            sprite,
            (self.sprite_width // 2, self.sprite_height // 2)
        )

        screen.blit(scaled_sprite, (
            screen_x - (self.sprite_width // 4),
            screen_y - (self.sprite_height // 4)
        ))

class Rabbit:
    """Třída reprezentující králíka - dekorativní NPC"""
    shared_sprite_sheet = None

    sprite_width = 48   # Match your sprite frame width
    sprite_height = 48  # Match your sprite frame height
    frame_count = 3     # Number of frames in the 6th row
    animation_row = 4.8  # Use the 6th row (index 5)

    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.target_position = Vector2(x, y)
        self.size = 8
        self.speed = 100
        self.color = (255, 255, 255)
        self.wander_timer = 0
        self.animation_timer = 0
        self.frame = 0
        self.last_direction_x = -1  # -1 = left, 1 = right (initial default facing left)

    def update(self, dt, player, world):
        """Aktualizace králíka"""
        self.animation_timer += dt
        if self.animation_timer > 0.2:
            self.frame = (self.frame + 1) % self.frame_count
            self.animation_timer = 0

        player_distance = GameEngine.distance(self.position, player.position)

        if player_distance < 40:
            escape_direction = self.position - player.position
            if escape_direction.magnitude() > 0:
                escape_direction = escape_direction.normalize()
                self.target_position = self.position + escape_direction * 100
        else:
            self.wander_timer += dt
            if self.wander_timer >= 3.0:
                offset_x = random.uniform(-50, 50)
                offset_y = random.uniform(-50, 50)
                self.target_position = Vector2(
                    self.position.x + offset_x,
                    self.position.y + offset_y
                )
                self.wander_timer = 0

        direction = self.target_position - self.position
        if direction.magnitude() > 2:
            direction = direction.normalize()
            new_pos = self.position + direction * self.speed * dt
            if not world.is_inside_fence(new_pos.x, new_pos.y, self.size):
                self.position = new_pos

            # Update last movement direction (left/right)
            if abs(direction.x) > 0.1:
                self.last_direction_x = 1 if direction.x > 0 else -1

    def render(self, screen, camera_x, camera_y):
        """Vykreslení králíka pomocí sprite sheetu"""
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        if Rabbit.shared_sprite_sheet is None:
            Rabbit.shared_sprite_sheet = pygame.image.load("assets/rabbit_sprite_sheet.png").convert_alpha()

        # Determine if rabbit is moving (i.e. animation vs idle)
        is_moving = (self.target_position - self.position).magnitude() > 2

        if is_moving:
            y_offset = int(self.sprite_height * self.animation_row)
            frame = self.frame
        else:
            y_offset = 0  # First row for idle
            frame = 0     # First frame

        frame_rect = pygame.Rect(
            frame * self.sprite_width,
            y_offset,
            self.sprite_width,
            self.sprite_height
        )

        sprite = Rabbit.shared_sprite_sheet.subsurface(frame_rect)

        # Flip sprite if facing right
        if self.last_direction_x > 0:
            sprite = pygame.transform.flip(sprite, True, False)

        # 🔽 SCALE DOWN: 50%
        scaled_sprite = pygame.transform.smoothscale(
            sprite,
            (self.sprite_width // 2, self.sprite_height // 2)
        )

        screen.blit(scaled_sprite, (
            screen_x - (self.sprite_width // 4),
            screen_y - (self.sprite_height // 4)
        ))


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
        for i in range(random.randint(8, 15)):
            x = random.uniform(0, self.world.world_width)
            y = random.uniform(0, self.world.world_height)
            self.goblins.append(Goblin(x, y))

        # Leprikónové (1-2)
        for i in range(random.randint(3, 4)):
            x = random.uniform(0, self.world.world_width)
            y = random.uniform(0, self.world.world_height)
            self.leprechauns.append(Leprechaun(x, y))

        # Medvědi (1-2)
        for i in range(random.randint(10, 15)):
            x = random.uniform(0, self.world.world_width)
            y = random.uniform(0, self.world.world_height)
            self.bears.append(Bear(x, y))

        # Lišky (2-4)
        for i in range(random.randint(14, 20)):
            x = random.uniform(0, self.world.world_width)
            y = random.uniform(0, self.world.world_height)
            self.foxes.append(Fox(x, y))

        # Králíci (3-6)
        for i in range(random.randint(10, 20)):
            x = random.uniform(0, self.world.world_width)
            y = random.uniform(0, self.world.world_height)
            self.rabbits.append(Rabbit(x, y))

    def update(self, dt, player, world):
        """Aktualizace všech NPC"""
        # Aktualizace goblinů
        for goblin in self.goblins[:]:  # Kopie seznamu pro bezpečné mazání
            goblin.update(dt, player, world)

        # Aktualizace leprikónů
        for leprechaun in self.leprechauns:
            leprechaun.update(dt, player, world)

        # Aktualizace medvědů
        for bear in self.bears:
            bear.update(dt, player, world)

        # Aktualizace lišek
        for fox in self.foxes:
            fox.update(dt, player, world)

        # Aktualizace králíků
        for rabbit in self.rabbits:
            rabbit.update(dt, player, world)

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
