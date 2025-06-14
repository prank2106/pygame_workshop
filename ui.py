import pygame
import math

class UI:
    """Třída pro uživatelské rozhraní"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

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
            'gray': (128, 128, 128),
            'dark_gray': (64, 64, 64),
            'light_gray': (192, 192, 192),
            'brown': (139, 69, 19),
            'gold': (255, 215, 0)
        }

        # UI panely
        self.hud_height = 120
        self.minimap_size = 150

    def draw_panel(self, surface, x, y, width, height, color, border_color=None, alpha=180):
        """Vykreslení panelu s průhledností"""
        panel = pygame.Surface((width, height))
        panel.set_alpha(alpha)
        panel.fill(color)
        surface.blit(panel, (x, y))

        if border_color:
            pygame.draw.rect(surface, border_color, (x, y, width, height), 2)

    def draw_progress_bar(self, surface, x, y, width, height, current, maximum, 
                         bg_color, fill_color, border_color=None):
        """Vykreslení progress baru"""
        # Pozadí
        pygame.draw.rect(surface, bg_color, (x, y, width, height))

        # Výplň
        if maximum > 0:
            fill_width = int((current / maximum) * width)
            pygame.draw.rect(surface, fill_color, (x, y, fill_width, height))

        # Okraj
        if border_color:
            pygame.draw.rect(surface, border_color, (x, y, width, height), 2)

    def render_hud(self, screen, player):
        """Vykreslení hlavního HUD"""
        # Hlavní HUD panel
        hud_y = self.screen_height - self.hud_height
        self.draw_panel(screen, 0, hud_y, self.screen_width, self.hud_height, 
                       self.colors['dark_gray'], self.colors['white'])

        # Zdraví
        health_x = 20
        health_y = hud_y + 20
        health_label = self.font_small.render("Zdraví:", True, self.colors['white'])
        screen.blit(health_label, (health_x, health_y))

        self.draw_progress_bar(screen, health_x, health_y + 20, 150, 15, 
                              player.health, player.max_health,
                              self.colors['red'], self.colors['green'], self.colors['white'])

        health_text = self.font_small.render(f"{player.health}/{player.max_health}", True, self.colors['white'])
        screen.blit(health_text, (health_x + 155, health_y + 18))

        # Energie
        energy_x = 20
        energy_y = hud_y + 60
        energy_label = self.font_small.render("Energie:", True, self.colors['white'])
        screen.blit(energy_label, (energy_x, energy_y))

        self.draw_progress_bar(screen, energy_x, energy_y + 20, 150, 15, 
                              player.energy, player.max_energy,
                              self.colors['gray'], self.colors['yellow'], self.colors['white'])

        energy_text = self.font_small.render(f"{player.energy}/{player.max_energy}", True, self.colors['white'])
        screen.blit(energy_text, (energy_x + 155, energy_y + 18))

        # Inventář
        inv_x = 350
        inv_y = hud_y + 20

        # Mince
        coins_text = self.font_medium.render(f"Mince: {player.coins}", True, self.colors['gold'])
        screen.blit(coins_text, (inv_x, inv_y))

        # Dřevo
        wood_text = self.font_medium.render(f"Dřevo: {player.wood}", True, self.colors['brown'])
        screen.blit(wood_text, (inv_x, inv_y + 25))

        # Jídlo a lektvary
        food_text = self.font_small.render(f"Jídlo: {player.food_count}", True, self.colors['white'])
        screen.blit(food_text, (inv_x, inv_y + 50))

        potion_text = self.font_small.render(f"Lektvary: {player.potion_count}", True, self.colors['white'])
        screen.blit(potion_text, (inv_x, inv_y + 70))

        # Vylepšení
        upgrades_x = 550
        upgrades_y = hud_y + 20

        upgrades_label = self.font_small.render("Vylepšení:", True, self.colors['white'])
        screen.blit(upgrades_label, (upgrades_x, upgrades_y))

        if player.has_better_axe:
            axe_text = self.font_small.render("✓ Lepší sekera", True, self.colors['green'])
            screen.blit(axe_text, (upgrades_x, upgrades_y + 20))

        if player.has_protection:
            protection_text = self.font_small.render(f"✓ Ochrana ({player.protection_timer:.0f}s)", True, self.colors['blue'])
            screen.blit(protection_text, (upgrades_x, upgrades_y + 40))

        # Cíl hry
        goal_x = 750
        goal_y = hud_y + 20
        goal_text = self.font_medium.render("CÍL:", True, self.colors['yellow'])
        screen.blit(goal_text, (goal_x, goal_y))

        target_text = self.font_small.render("500 mincí", True, self.colors['white'])
        screen.blit(target_text, (goal_x, goal_y + 25))

        progress_text = self.font_small.render(f"Pokrok: {(player.coins/500)*100:.1f}%", True, self.colors['white'])
        screen.blit(progress_text, (goal_x, goal_y + 45))

    def render_minimap(self, screen, player, npc_manager, world):
        """Vykreslení minimapy"""
        minimap_x = self.screen_width - self.minimap_size - 20
        minimap_y = 20

        # Pozadí minimapy
        self.draw_panel(screen, minimap_x, minimap_y, self.minimap_size, self.minimap_size,
                       self.colors['dark_gray'], self.colors['white'])

        # Nadpis
        title_text = self.font_small.render("Mapa", True, self.colors['white'])
        screen.blit(title_text, (minimap_x + 5, minimap_y + 5))

        # Měřítko minimapy
        scale_x = (self.minimap_size - 20) / world.world_width
        scale_y = (self.minimap_size - 20) / world.world_height

        # Pozice hráče na minimapě
        player_map_x = int(minimap_x + 10 + player.position.x * scale_x)
        player_map_y = int(minimap_y + 20 + player.position.y * scale_y)

        # Vykreslení stromů na minimapě
        for tree in world.trees[:50]:  # Pouze prvních 50 pro výkon
            tree_map_x = int(minimap_x + 10 + tree.position.x * scale_x)
            tree_map_y = int(minimap_y + 20 + tree.position.y * scale_y)

            if tree.tree_type == "big":
                pygame.draw.circle(screen, self.colors['green'], (tree_map_x, tree_map_y), 2)
            else:
                pygame.draw.circle(screen, self.colors['green'], (tree_map_x, tree_map_y), 1)

        # Vykreslení NPC na minimapě
        # Goblinové
        for goblin in npc_manager.goblins:
            goblin_map_x = int(minimap_x + 10 + goblin.position.x * scale_x)
            goblin_map_y = int(minimap_y + 20 + goblin.position.y * scale_y)
            pygame.draw.circle(screen, (139, 0, 139), (goblin_map_x, goblin_map_y), 2)

        # Leprikónové
        for leprechaun in npc_manager.leprechauns:
            lep_map_x = int(minimap_x + 10 + leprechaun.position.x * scale_x)
            lep_map_y = int(minimap_y + 20 + leprechaun.position.y * scale_y)
            pygame.draw.circle(screen, self.colors['green'], (lep_map_x, lep_map_y), 2)

        # Medvědi
        for bear in npc_manager.bears:
            bear_map_x = int(minimap_x + 10 + bear.position.x * scale_x)
            bear_map_y = int(minimap_y + 20 + bear.position.y * scale_y)
            pygame.draw.circle(screen, self.colors['brown'], (bear_map_x, bear_map_y), 3)

        # Hráč (nakonec, aby byl vidět)
        pygame.draw.circle(screen, self.colors['blue'], (player_map_x, player_map_y), 4)
        pygame.draw.circle(screen, self.colors['white'], (player_map_x, player_map_y), 4, 1)

    def render_help_panel(self, screen):
        """Vykreslení nápovědy"""
        help_x = 20
        help_y = 20
        help_width = 300
        help_height = 200

        self.draw_panel(screen, help_x, help_y, help_width, help_height,
                       self.colors['dark_gray'], self.colors['white'])

        # Nadpis
        title_text = self.font_medium.render("Ovládání", True, self.colors['yellow'])
        screen.blit(title_text, (help_x + 10, help_y + 10))

        # Seznam ovládacích prvků
        controls = [
            "Šipky - Pohyb",
            "MEZERNÍK - Kácení stromu",
            "P - Prodej dřeva",
            "B - Otevřít obchod",
            "1-4 - Rychlé nákupy",
            "E - Použít jídlo",
            "H - Použít lektvar",
            "G - Chytit goblina",
            "L - Interakce s leprikónem"
        ]

        y_offset = help_y + 40
        for control in controls:
            control_text = self.font_small.render(control, True, self.colors['white'])
            screen.blit(control_text, (help_x + 10, y_offset))
            y_offset += 18

    def render_status_messages(self, screen, messages):
        """Vykreslení stavových zpráv"""
        if not messages:
            return

        y_offset = 100
        for message, color, timer in messages:
            if timer > 0:
                alpha = min(255, int(timer * 85))  # Fade out efekt
                text_surface = self.font_medium.render(message, True, color)

                # Pozadí zprávy
                text_rect = text_surface.get_rect(center=(self.screen_width//2, y_offset))
                bg_rect = text_rect.inflate(20, 10)

                bg_surface = pygame.Surface(bg_rect.size)
                bg_surface.set_alpha(alpha // 2)
                bg_surface.fill(self.colors['black'])
                screen.blit(bg_surface, bg_rect.topleft)

                # Text zprávy
                text_surface.set_alpha(alpha)
                screen.blit(text_surface, text_rect)

                y_offset += 35

    def render_debug_info(self, screen, player, fps):
        """Vykreslení debug informací"""
        debug_x = 20
        debug_y = self.screen_height - 200

        debug_info = [
            f"FPS: {fps:.1f}",
            f"Pozice: ({player.position.x:.1f}, {player.position.y:.1f})",
            f"Rychlost: {player.velocity.magnitude():.1f}",
            f"Catch cooldown: {player.catch_cooldown:.1f}s"
        ]

        for i, info in enumerate(debug_info):
            text = self.font_small.render(info, True, self.colors['white'])
            screen.blit(text, (debug_x, debug_y + i * 20))

    def render_interaction_prompts(self, screen, player, npc_manager, trader_pos, shop_system):
        """Vykreslení promptů pro interakci"""
        prompts = []

        # Prompt pro obchodníka
        if shop_system.is_trader_nearby(player.position, trader_pos):
            prompts.append("P - Prodej dřeva | B - Obchod | 1-4 - Rychlé nákupy")

        # Prompt pro goblina
        from game_engine import GameEngine
        for goblin in npc_manager.goblins:
            if GameEngine.distance(player.position, goblin.position) < 50:
                prompts.append("G - Chytit goblina")
                break

        # Prompt pro leprikóna
        for leprechaun in npc_manager.leprechauns:
            if GameEngine.distance(player.position, leprechaun.position) < 50:
                prompts.append("L - Interakce s leprikónem")
                break

        # Vykreslení promptů
        if prompts:
            y_offset = self.screen_height // 2
            for prompt in prompts:
                text = self.font_medium.render(prompt, True, self.colors['yellow'])
                text_rect = text.get_rect(center=(self.screen_width//2, y_offset))

                # Pozadí
                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
                pygame.draw.rect(screen, self.colors['yellow'], bg_rect, 2)

                screen.blit(text, text_rect)
                y_offset += 40
