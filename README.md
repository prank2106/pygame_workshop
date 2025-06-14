# Forest Lumberjack - Dřevorubec v lese
## Pygame hra s využitím knihoven Pygame a NumPy

### Popis hry
Forest Lumberjack je 2D hra, ve které hráč ovládá dřevorubce v lese. Cílem hry je nasbírat 500 mincí prostřednictvím kácení stromů, prodeje dřeva a interakcí s různými postavami v lese. Hráč musí dávat pozor na nepřátelské bytosti, které ho mohou ohrozit nebo okrást.

### Instalace a spuštění

#### Rychlé spuštění
```bash
python launch_game.py
```

#### Ruční instalace
1. Ujistěte se, že máte nainstalovaný Python 3.7 nebo novější
2. Nainstalujte potřebné knihovny:
   ```
   pip install pygame numpy
   ```
3. Stáhněte všechny soubory hry
4. Spusťte hru příkazem:
   ```
   python main.py
   ```

### Ovládání
- **Šipky (↑↓←→)**: Pohyb dřevorubce
- **Mezerník (SPACE)**: Kácení stromu
- **P**: Prodej dřeva (když jste u obchodníka)
- **B**: Otevření obchodu (když jste u obchodníka)
- **1-4**: Rychlé nákupy v obchodě (když jste u obchodníka)
  - **1**: Nákup jídla (10 mincí)
  - **2**: Nákup lektvaru (20 mincí)
  - **3**: Nákup lepší sekery (50 mincí)
  - **4**: Nákup ochrany (30 mincí)
- **E**: Použití jídla (doplnění energie)
- **H**: Použití lektvaru (doplnění zdraví)
- **G**: Pokus o chytání goblina
- **L**: Interakce s leprikónem
- **ESC**: Menu / Ukončení

### Herní mechaniky

#### Kácení stromů
V lese se nacházejí dva typy stromů:
- **Malé stromy**: Vyžadují jedno seknutí a poskytují 1-3 kusy dřeva
- **Velké stromy**: Vyžadují více seknutí a poskytují 5 kusů dřeva

Pro kácení stromů je potřeba energie, která se postupně regeneruje.

#### Ekonomika
- Dřevo lze prodat obchodníkovi za 5 mincí za kus
- Za získané mince lze nakoupit:
  - **Jídlo (10 mincí)**: Doplní 40 energie
  - **Lektvar (20 mincí)**: Doplní 50 zdraví
  - **Lepší sekera (50 mincí)**: Rychlejší kácení a pohyb
  - **Ochrana (30 mincí)**: Poloviční poškození na 60 sekund

#### Postavy v lese

##### Přátelské/Neutrální
- **Obchodník**: Vykupuje dřevo a prodává předměty (zlatá barva)
- **Leprikón**: Dává odměny (peníze, dřevo, zdraví) nebo teleportuje hráče (zelená, blikající)
- **Králík**: Dekorativní prvek, utíká před hráčem (bílá)

##### Nepřátelské
- **Goblin**: Krade peníze nebo dřevo, lze ho chytit a získat odměnu (fialová)
- **Medvěd**: Útočí na hráče a snižuje jeho zdraví (hnědá)
- **Liška**: Rychle krade mince (oranžová)

### Herní cíl
Hra má dva možné konce:
1. **Vítězství**: Hráč nasbírá cílový počet mincí (500)
2. **Prohra**: Hráč ztratí všechny životy

### Struktura projektu
```
Forest_Lumberjack/
├── main.py              # Hlavní herní soubor
├── game_engine.py       # Herní engine a utility funkce
├── player.py            # Třída hráče
├── world.py             # Generování herního světa
├── npc_manager.py       # Správa NPC postav
├── ui.py                # Uživatelské rozhraní
├── shop_system.py       # Obchodní systém
├── test_game.py         # Testovací skripty
├── launch_game.py       # Spouštěcí script
├── requirements.txt     # Závislosti
└── README.md           # Tato dokumentace
```

### Technické detaily

#### Použité knihovny
- **Pygame**: Grafika, input handling, herní smyčka
- **NumPy**: Matematické výpočty a optimalizace
- **Math**: Trigonometrické funkce
- **Random**: Náhodné generování

#### Klíčové funkce
- **Procedurální generování světa** pomocí šumových map
- **AI chování NPC** pomocí stavových automatů
- **Optimalizované vykreslování** s culling objektů mimo obrazovku
- **Modulární architektura** pro snadnou rozšiřitelnost

### Řešení problémů

#### Časté problémy
1. **ImportError**: Ujistěte se, že máte nainstalované pygame a numpy
2. **Chyba při spuštění**: Zkontrolujte Python verzi (potřeba 3.7+)
3. **Pomalý výkon**: Zkuste snížit počet objektů ve world.py

#### Debug režim
Pro zobrazení debug informací upravte ui.py a zavolejte render_debug_info().

### Možná rozšíření
- Více typů stromů a materiálů
- Systém craftingu
- Více typů NPC a interakcí
- Save/Load systém
- Multiplayer podpora
- Zvukové efekty a hudba

### Technické specifikace
- **Minimální rozlišení**: 1024x768
- **FPS**: 60
- **Velikost světa**: 2048x1536 pixelů
- **Počet NPC**: 8-16 podle typu
- **Počet stromů**: 150-250

### Changelog

#### Verze 1.1 (Opravy)
- ✅ Opraveno chytání goblina (klávesa G)
- ✅ Opraveno vylepšování sekery v obchodě
- ✅ Přidány rychlé nákupy (klávesy 1-4)
- ✅ Vylepšené UI a feedback pro hráče
- ✅ Optimalizovaný kód a odstranění chyb

#### Verze 1.0 (Původní)
- Základní implementace hry
- Všechny hlavní mechaniky

### Kontakt a podpora
Pro hlášení chyb nebo návrhy na vylepšení vytvořte issue nebo kontaktujte vývojáře.

### License
Tento projekt je vytvořen pro vzdělávací účely.
