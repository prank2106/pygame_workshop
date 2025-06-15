import pygame
from game_engine import Vector2, GameEngine

class ShopSystem:
    """Třída pro správu obchodu"""

    def __init__(self):
        self.shop_items = {
            "food": {
                "name": "Jídlo",
                "price": 10,
                "description": "Doplní 40 energie"
            },
            "potion": {
                "name": "Lektvar",
                "price": 20,
                "description": "Doplní 50 zdraví"
            },
            "better_axe": {
                "name": "Lepší sekera",
                "price": 50,
                "description": "Rychlejší kácení a pohyb"
            },
            "protection": {
                "name": "Ochrana",
                "price": 30,
                "description": "Poloviční poškození na 60 sekund"
            }
        }

        # Fonty
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

        # Barvy
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'gold': (255, 215, 0),
            'gray': (128, 128, 128),
            'dark_gray': (64, 64, 64)
        }

        # Aktivní flag pro zobrazení
        self.shop_active = False
        self.selected_item = None
        self.transaction_message = None
        self.message_timer = 0

    def update(self, dt):
        """Aktualizace shop systému"""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.transaction_message = None

    def is_trader_nearby(self, player_pos, trader_pos, radius=50):
        """Kontrola, zda je hráč blízko obchodníka"""
        distance = GameEngine.distance(player_pos, trader_pos)
        return distance <= radius

    def open_shop(self):
        """Otevření obchodu"""
        self.shop_active = True

    def close_shop(self):
        """Zavření obchodu"""
        self.shop_active = False

    def sell_wood(self, player):
        """Prodej dřeva hráče obchodníkovi"""
        if player.wood <= 0:
            self.show_message("Nemáš žádné dřevo k prodeji!", self.colors['red'])
            return False

        coins_earned = player.wood * 5  # 5 mincí za kus dřeva
        player.coins += coins_earned
        wood_sold = player.wood
        player.wood = 0

        self.show_message(f"Prodal jsi {wood_sold} dřeva za {coins_earned} mincí!", self.colors['green'])
        return True

    def buy_item(self, player, item_key):
        """OPRAVA: Kompletní nákupní logika"""
        if item_key not in self.shop_items:
            self.show_message("Neznámý předmět!", self.colors['red'])
            return False

        item = self.shop_items[item_key]

        # Kontrola, zda má hráč dostatek peněz
        if player.coins < item["price"]:
            self.show_message(f"Nemáš dostatek mincí! Potřebuješ {item['price']} mincí.", self.colors['red'])
            return False

        # Speciální kontroly pro některé předměty
        if item_key == "better_axe" and player.has_better_axe:
            self.show_message("Už máš lepší sekeru!", self.colors['red'])
            return False

        if item_key == "protection" and player.has_protection:
            self.show_message("Už máš aktivní ochranu!", self.colors['red'])
            return False

        # Provedení transakce
        player.coins -= item["price"]

        # OPRAVA: Správné přidání předmětu podle typu
        if item_key == "food":
            player.add_item("food", 1)
            self.show_message(f"Koupil jsi {item['name']} za {item['price']} mincí!", self.colors['green'])
        elif item_key == "potion":
            player.add_item("potion", 1)
            self.show_message(f"Koupil jsi {item['name']} za {item['price']} mincí!", self.colors['green'])
        elif item_key == "better_axe":
            player.add_item("better_axe")
            self.show_message(f"Koupil jsi {item['name']} za {item['price']} mincí!", self.colors['green'])
        elif item_key == "protection":
            player.add_item("protection")
            self.show_message(f"Koupil jsi {item['name']} za {item['price']} mincí!", self.colors['green'])

        return True

    def show_message(self, message, color):
        """Zobrazení zprávy"""
        self.transaction_message = (message, color)
        self.message_timer = 3.0  # 3 sekundy

    def render_shop_ui(self, screen, player):
        """Vykreslení obchodního UI"""
        # Informace o blízkosti obchodníka
        info_text = self.font_small.render("U obchodníka - P: Prodej dřeva, B: Obchod, 1-4: Rychlé nákupy", True, self.colors['white'])
        screen.blit(info_text, (10, 10))

        # Panel s cenami a klávesami
        panel_y = 40
        self.draw_panel(screen, 10, panel_y, 400, 120, self.colors['dark_gray'], self.colors['white'])

        # Nadpis
        title_text = self.font_medium.render("OBCHOD", True, self.colors['gold'])
        screen.blit(title_text, (20, panel_y + 10))

        # Seznam předmětů s klávesami
        items_info = [
            ("1", "food", f"Jídlo - {self.shop_items['food']['price']} mincí"),
            ("2", "potion", f"Lektvar - {self.shop_items['potion']['price']} mincí"),
            ("3", "better_axe", f"Lepší sekera - {self.shop_items['better_axe']['price']} mincí"),
            ("4", "protection", f"Ochrana - {self.shop_items['protection']['price']} mincí")
        ]

        y_offset = panel_y + 35
        for key, item_key, text in items_info:
            # Barva podle dostupnosti
            color = self.colors['white']
            if player.coins < self.shop_items[item_key]["price"]:
                color = self.colors['red']
            elif (item_key == "better_axe" and player.has_better_axe) or \
                 (item_key == "protection" and player.has_protection):
                color = self.colors['gray']

            item_text = self.font_small.render(f"{key}: {text}", True, color)
            screen.blit(item_text, (20, y_offset))
            y_offset += 20

        # Zobrazení zpráv o transakcích
        if self.transaction_message:
            message_text, message_color = self.transaction_message
            text_surface = self.font_medium.render(message_text, True, message_color)
            text_rect = text_surface.get_rect(center=(screen.get_width()//2, 200))

            # Pozadí zprávy
            pygame.draw.rect(screen, (0, 0, 0, 180), text_rect.inflate(20, 10))
            screen.blit(text_surface, text_rect)

    def draw_panel(self, surface, x, y, width, height, color, border_color=None, alpha=180):
        """Vykreslení panelu s průhledností"""
        panel = pygame.Surface((width, height))
        panel.set_alpha(alpha)
        panel.fill(color)
        surface.blit(panel, (x, y))

        if border_color:
            pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
