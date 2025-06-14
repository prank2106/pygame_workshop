import os
import sys
import importlib

class GameTester:
    """Testovací třída pro ověření funkčnosti hry"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def run_test(self, test_name, test_function):
        """Spuštění jednotlivého testu"""
        try:
            test_function()
            self.tests_passed += 1
            self.results.append(f"✅ {test_name}: PROŠEL")
            print(f"✅ {test_name}: PROŠEL")
        except Exception as e:
            self.tests_failed += 1
            self.results.append(f"❌ {test_name}: SELHAL - {str(e)}")
            print(f"❌ {test_name}: SELHAL - {str(e)}")

    def test_python_version(self):
        """Test verze Pythonu"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            raise Exception(f"Python {version.major}.{version.minor} není podporován. Potřeba Python 3.7+")

    def test_imports(self):
        """Test importu všech modulů"""
        required_modules = [
            'pygame',
            'numpy',
            'math',
            'random',
            'sys',
            'os'
        ]

        for module in required_modules:
            importlib.import_module(module)

    def test_game_files(self):
        """Test existence herních souborů"""
        required_files = [
            'main.py',
            'game_engine.py',
            'player.py',
            'world.py',
            'npc_manager.py',
            'ui.py',
            'shop_system.py',
            'README.md'
        ]

        for file in required_files:
            if not os.path.exists(file):
                raise Exception(f"Chybí soubor: {file}")

    def test_pygame_initialization(self):
        """Test inicializace Pygame"""
        import pygame
        pygame.init()

        # Test vytvoření displeje
        screen = pygame.display.set_mode((100, 100))
        pygame.display.set_caption("Test")

        # Ukončení testu
        pygame.quit()

    def test_game_modules_import(self):
        """Test importu herních modulů"""
        game_modules = [
            'game_engine',
            'player',
            'world',
            'npc_manager',
            'ui',
            'shop_system'
        ]

        for module in game_modules:
            importlib.import_module(module)

    def test_basic_functionality(self):
        """Test základní funkčnosti"""
        # Test game_engine
        from game_engine import GameEngine, Vector2

        # Test Vector2
        v1 = Vector2(3, 4)
        v2 = Vector2(1, 1)
        v3 = v1 + v2

        if abs(v3.x - 4) > 0.001 or abs(v3.y - 5) > 0.001:
            raise Exception("Vector2 addition failed")

        if abs(v1.magnitude() - 5.0) > 0.001:
            raise Exception("Vector2 magnitude calculation failed")

        # Test distance calculation
        distance = GameEngine.distance(Vector2(0, 0), Vector2(3, 4))
        if abs(distance - 5.0) > 0.001:
            raise Exception("Distance calculation failed")

    def test_class_instantiation(self):
        """Test vytvoření instancí hlavních tříd"""
        from game_engine import Vector2
        from player import Player
        from world import World
        from npc_manager import NPCManager
        from ui import UI
        from shop_system import ShopSystem

        # Test Player
        player = Player(100, 100)
        if player.position.x != 100 or player.position.y != 100:
            raise Exception("Player creation failed")

        # Test World
        world = World(800, 600)
        if len(world.trees) == 0:
            raise Exception("World generation failed - no trees")

        # Test NPCManager
        npc_manager = NPCManager(world)
        if len(npc_manager.goblins) == 0:
            raise Exception("NPC generation failed - no goblins")

        # Test UI
        ui = UI(800, 600)
        if ui.screen_width != 800:
            raise Exception("UI creation failed")

        # Test ShopSystem
        shop = ShopSystem()
        if "better_axe" not in shop.shop_items:
            raise Exception("Shop system failed - missing better_axe")

    def run_all_tests(self):
        """Spuštění všech testů"""
        print("🔍 Spouštění testů Forest Lumberjack...")
        print("=" * 50)

        self.run_test("Python verze", self.test_python_version)
        self.run_test("Import základních modulů", self.test_imports)
        self.run_test("Existence herních souborů", self.test_game_files)
        self.run_test("Pygame inicializace", self.test_pygame_initialization)
        self.run_test("Import herních modulů", self.test_game_modules_import)
        self.run_test("Základní funkcionalita", self.test_basic_functionality)
        self.run_test("Vytvoření instancí tříd", self.test_class_instantiation)

        print("=" * 50)
        print(f"📊 Výsledky testů:")
        print(f"   ✅ Prošlo: {self.tests_passed}")
        print(f"   ❌ Selhalo: {self.tests_failed}")
        print(f"   📈 Úspěšnost: {(self.tests_passed/(self.tests_passed+self.tests_failed)*100):.1f}%")

        if self.tests_failed == 0:
            print("🎉 Všechny testy prošly! Hra je připravena ke spuštění.")
            return True
        else:
            print("⚠️ Některé testy selhaly. Zkontrolujte chyby výše.")
            return False

if __name__ == "__main__":
    tester = GameTester()
    success = tester.run_all_tests()

    if success:
        print("\n🚀 Můžete spustit hru příkazem: python main.py")
    else:
        print("\n🔧 Před spuštěním hry opravte výše uvedené problémy.")

    sys.exit(0 if success else 1)
