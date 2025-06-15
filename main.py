import pygame
import sys
import math
import random
from enum import Enum

# Import herních modulů
from game_engine import GameEngine, Vector2
from player import Player
from world import World
from npc_manager import NPCManager
from ui import UI
from shop_system import ShopSystem

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    VICTORY = 5

class ForestLumberjack:
    def __init__(self):
        pygame.init()
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Forest Lumberjack - Dřevorubec v lese")
        self.trader_image = pygame.image.load("assets/props_camping_tent_02.png").convert_alpha()


        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState.MENU

        # Barvy
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'green': (34, 139, 34),
            'brown': (139, 69, 19),
            'dark_green': (0, 100, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'gray': (128, 128, 128)
        }

        # Fonty
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Inicializace herních systémů
        self.camera_x = 0
        self.camera_y = 0
        self.target_coins = 500

    def init_game(self):
        """Inicializace nové hry"""
        self.world = World(self.screen_width, self.screen_height)

        #Nalezení bezpečného místa pro spawn hráče
        spawn_x, spawn_y = self.find_spawn_point()
        self.player = Player(spawn_x, spawn_y, self.world)

        self.npc_manager = NPCManager(self.world)
        self.ui = UI(self.screen_width, self.screen_height)
        self.shop_system = ShopSystem()

        # Umístění obchodníka
        self.trader_pos = Vector2(200, 200)

        # Kamera
        self.camera_x = self.player.position.x - self.screen_width // 2
        self.camera_y = self.player.position.y - self.screen_height // 2

    def find_spawn_point(self):
        """🔍 Hledání bezpečného místa pro spawn hráče"""
        for _ in range(1000):  # Zkus až 1000 různých pozic
            x = random.uniform(100, self.world.world_width - 100)
            y = random.uniform(100, self.world.world_height - 100)
            if self.world.is_position_walkable(x, y, radius=15):  #Kontrola kolizí
                return x, y
        print("Nenašel se volný spawn point, používá se default.")
        return 400, 300  # záložní bod, pokud vše selže

    def handle_events(self):
        """Zpracování událostí"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.game_state = GameState.PLAYING
                        self.init_game()
                elif self.game_state == GameState.PLAYING:
                    self.handle_game_input(event)
                elif self.game_state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_RETURN:
                        self.game_state = GameState.MENU

    def handle_game_input(self, event):
        """Zpracování herního vstupu"""
        if event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
        elif event.key == pygame.K_SPACE:
            # Kácení stromu
            self.player.try_chop_tree(self.world.trees)
        elif event.key == pygame.K_p:
            # Prodej dřeva
            if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
                self.shop_system.sell_wood(self.player)
        elif event.key == pygame.K_e:
            # Použití jídla
            self.player.use_food()
        elif event.key == pygame.K_h:
            # Použití lektvaru
            self.player.use_potion()
        elif event.key == pygame.K_g:
            # OPRAVA: Chytání goblina
            self.player.try_catch_goblin(self.npc_manager.goblins)
        elif event.key == pygame.K_l:
            # Interakce s leprikónem
            self.player.interact_with_leprechaun(self.npc_manager.leprechauns)
        elif event.key == pygame.K_b:
            # OPRAVA: Otevření obchodu pro nákup
            if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
                self.shop_system.open_shop()
        elif event.key == pygame.K_1:
            # Nákup jídla
            if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
                self.shop_system.buy_item(self.player, "food")
        elif event.key == pygame.K_2:
            # Nákup lektvaru
            if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
                self.shop_system.buy_item(self.player, "potion")
        elif event.key == pygame.K_3:
            # OPRAVA: Nákup lepší sekery
            if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
                self.shop_system.buy_item(self.player, "better_axe")
        elif event.key == pygame.K_4:
            # Nákup ochrany
            if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
                self.shop_system.buy_item(self.player, "protection")

    def update_game(self, dt):
        """Aktualizace herní logiky"""
        if self.game_state != GameState.PLAYING:
            return

        # Zpracování vstupu pro pohyb
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # Aktualizace herních objektů
        self.player.update(dt)
        self.world.update(dt)
        self.npc_manager.update(dt, self.player, self.world)
        self.shop_system.update(dt)

        # Aktualizace kamery
        self.update_camera()

        # Kontrola vítězných/prohraných podmínek
        self.check_game_conditions()

    def update_camera(self):
        """Aktualizace kamery pro sledování hráče"""
        target_x = self.player.position.x - self.screen_width // 2
        target_y = self.player.position.y - self.screen_height // 2

        # Plynulé sledování
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1

    def check_game_conditions(self):
        """Kontrola vítězných a prohraných podmínek"""
        if self.player.coins >= self.target_coins:
            self.game_state = GameState.VICTORY
        elif self.player.health <= 0:
            self.game_state = GameState.GAME_OVER

    def render(self):
        """Vykreslení hry"""
        self.screen.fill(self.colors['dark_green'])

        if self.game_state == GameState.MENU:
            self.render_menu()
        elif self.game_state == GameState.PLAYING:
            self.render_game()
        elif self.game_state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.game_state == GameState.VICTORY:
            self.render_victory()

        pygame.display.flip()

    def render_menu(self):
        """Vykreslení úvodní obrazovky"""
        # Pozadí
        self.screen.fill((0, 50, 0))

        # Titulní text
        title_text = self.font_large.render("Forest Lumberjack", True, self.colors['white'])
        subtitle_text = self.font_medium.render("Dřevorubec v lese", True, self.colors['yellow'])

        title_rect = title_text.get_rect(center=(self.screen_width//2, 150))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width//2, 200))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)

        # Instrukce
        instructions = [
    f"Cíl hry: Nasbírej {self.target_coins} mincí",
            "",
            "Ovládání aka Controls:",
            "Šipky - pohyb",
            "MEZERNÍK - kácení stromu",
            "P jako Prodat, prodej dřevo obchodníkovi",
            "B jako Buy, otevři nabídku obchodníka",
            "1-4 - nákup předmětu u obchodníka",
            "E jako Eat, použít jídlo",
            "H jako Heal, použít lektvar",
            "G jako Goblin, chytit goblina",
            "L jako Leprikón, interakce s leprikónem",
            "",
            "Pozor na nebezpečná stvoření!",
            "",
            "Popadni sekeru, stiskni ENTER a hurá do lesa!",
]

        y_offset = 280
        for instruction in instructions:
            color = self.colors['white'] if instruction else self.colors['white']
            if "Pozor" in instruction:
                color = self.colors['red']
            elif "Stiskni ENTER" in instruction:
                color = self.colors['yellow']

            text = self.font_small.render(instruction, True, color)
            text_rect = text.get_rect(center=(self.screen_width//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25

    def render_game(self):
        """Vykreslení hry"""
        # Vykreslení světa
        self.world.render(self.screen, self.camera_x, self.camera_y)

        # Vykreslení obchodníka
        trader_x = int(self.trader_pos.x - self.camera_x)
        trader_y = int(self.trader_pos.y - self.camera_y)
        tent_rect = self.trader_image.get_rect(center=(trader_x, trader_y))
        self.screen.blit(self.trader_image, tent_rect)


        # Vykreslení NPC
        self.npc_manager.render(self.screen, self.camera_x, self.camera_y)

        # Vykreslení hráče
        self.player.render(self.screen, self.camera_x, self.camera_y)

        # Vykreslení UI
        self.ui.render_hud(self.screen, self.player)
        self.ui.render_minimap(self.screen, self.player, self.npc_manager, self.world)

        # Vykreslení shop systému
        if self.shop_system.is_trader_nearby(self.player.position, self.trader_pos):
            self.shop_system.render_shop_ui(self.screen, self.player)

    def render_game_over(self):
        """Vykreslení obrazovky game over"""
        self.screen.fill((50, 0, 0))

        game_over_text = self.font_large.render("GAME OVER", True, self.colors['red'])
        reason_text = self.font_medium.render("Ztratil jsi všechny životy!", True, self.colors['white'])
        restart_text = self.font_small.render("Stiskni ENTER pro návrat do menu", True, self.colors['yellow'])

        self.screen.blit(game_over_text, game_over_text.get_rect(center=(self.screen_width//2, 300)))
        self.screen.blit(reason_text, reason_text.get_rect(center=(self.screen_width//2, 350)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(self.screen_width//2, 450)))

    def render_victory(self):
        """Vykreslení vítězné obrazovky"""
        self.screen.fill((0, 50, 0))

        victory_text = self.font_large.render("VÍTĚZSTVÍ!", True, self.colors['yellow'])
        reason_text = self.font_medium.render(f"Nasbíral jsi {self.target_coins} mincí!", True, self.colors['white'])
        restart_text = self.font_small.render("Stiskni ENTER pro návrat do menu", True, self.colors['yellow'])

        self.screen.blit(victory_text, victory_text.get_rect(center=(self.screen_width//2, 300)))
        self.screen.blit(reason_text, reason_text.get_rect(center=(self.screen_width//2, 350)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(self.screen_width//2, 450)))

    def run(self):
        """Hlavní herní smyčka"""
        dt = 0.016  # ~60 FPS

        while self.running:
            self.handle_events()
            self.update_game(dt)
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ForestLumberjack()
    game.run()
