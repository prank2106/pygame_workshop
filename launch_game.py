#!/usr/bin/env python3
import os
import sys
import subprocess
import importlib.util
import platform

def check_python_version():
    """Kontrola verze Pythonu"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} není podporován.")
        print("⚠️ Pro spuštění hry je potřeba Python 3.7 nebo novější.")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} je kompatibilní.")
    return True

def check_dependencies():
    """Kontrola nainstalovaných knihoven"""
    required_modules = {
        "pygame": "pygame",
        "numpy": "numpy"
    }

    missing_modules = []

    for module_name, package_name in required_modules.items():
        if importlib.util.find_spec(module_name) is None:
            missing_modules.append(package_name)

    if missing_modules:
        print(f"❌ Chybí některé knihovny: {', '.join(missing_modules)}")

        choice = input("Chcete je nainstalovat nyní? (a/n): ").lower()
        if choice == 'a' or choice == 'y' or choice == '':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_modules)
                print("✅ Všechny závislosti byly nainstalovány.")
                return True
            except subprocess.CalledProcessError:
                print("❌ Instalace selhala.")
                print("⚠️ Prosím, nainstalujte knihovny ručně: pip install pygame numpy")
                return False
        else:
            print("⚠️ Prosím, nainstalujte knihovny ručně: pip install pygame numpy")
            return False

    print("✅ Všechny závislosti jsou nainstalovány.")
    return True

def check_game_files():
    """Kontrola, zda existují všechny herní soubory"""
    required_files = [
        'main.py',
        'game_engine.py',
        'player.py',
        'world.py',
        'npc_manager.py',
        'ui.py',
        'shop_system.py'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Chybí herní soubory: {', '.join(missing_files)}")
        return False

    print("✅ Všechny herní soubory jsou k dispozici.")
    return True

def run_tests():
    """Spuštění testů"""
    print("🔍 Spouštění testů...")
    try:
        import test_game
        tester = test_game.GameTester()
        return tester.run_all_tests()
    except ImportError:
        print("⚠️ Test soubor není k dispozici, přeskakuji testy.")
        return True
    except Exception as e:
        print(f"❌ Chyba při testování: {e}")
        return False

def launch_game():
    """Spuštění hlavní hry"""
    print("🚀 Spouštím Forest Lumberjack...")
    try:
        import main
        game = main.ForestLumberjack()
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Hra byla ukončena uživatelem.")
    except Exception as e:
        print(f"❌ Chyba při spuštění hry: {e}")
        print("💡 Zkuste spustit: python main.py")
        return False

    return True

def main():
    """Hlavní funkce spouštěče"""
    print("=" * 60)
    print("🌲 FOREST LUMBERJACK - SPOUŠTĚČ HRY 🌲")
    print("=" * 60)

    # Kontrola Python verze
    if not check_python_version():
        return False

    print()

    # Kontrola závislostí
    if not check_dependencies():
        return False

    print()

    # Kontrola herních souborů
    if not check_game_files():
        return False

    print()

    # Volitelné spuštění testů
    run_tests_choice = input("Chcete spustit testy před zahájením hry? (a/n): ").lower()
    if run_tests_choice == 'a' or run_tests_choice == 'y' or run_tests_choice == '':
        if not run_tests():
            print("⚠️ Některé testy selhaly, ale hra může stále fungovat.")
            continue_choice = input("Chcete pokračovat ve spuštění hry? (a/n): ").lower()
            if continue_choice != 'a' and continue_choice != 'y' and continue_choice != '':
                return False
        print()

    # Zobrazení informací o systému
    print("📋 Informace o systému:")
    print(f"   🖥️ OS: {platform.system()} {platform.release()}")
    print(f"   🐍 Python: {sys.version.split()[0]}")
    try:
        import pygame
        print(f"   🎮 Pygame: {pygame.version.ver}")
    except:
        pass
    try:
        import numpy
        print(f"   🔢 NumPy: {numpy.__version__}")
    except:
        pass

    print()
    print("🎯 Připraven ke spuštění!")
    input("Stiskněte ENTER pro zahájení hry...")

    # Spuštění hry
    return launch_game()

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Hra byla ukončena úspěšně.")
        else:
            print("\n❌ Vyskytl se problém při spuštění hry.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Spuštění zrušeno uživatelem.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Neočekávaná chyba: {e}")
        sys.exit(1)
