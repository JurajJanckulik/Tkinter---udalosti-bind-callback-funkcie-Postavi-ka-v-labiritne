# Líška v bludisku

Doveď líšku k zlatému lampášu v desiatich náhodne generovaných bludiskách. Zamknuté mreže rozdeľujú les na časti. Na druhú stranu sa dostaneš portálom s rovnakým písmenom.

## Spustenie v PhpStorme

Potrebuješ **Python 3 s Tkinterom**. Celá hra vrátane grafiky je v súbore `bludisko.py`.

1. Ulož `bludisko.py` do priečinka projektu. V PhpStorme otvor tento priečinok.
2. Otvor **Terminal** v priečinku, kde je uložený súbor.
3. Spusť príkaz pre svoj systém.

| Systém | Príkaz |
| --- | --- |
| Windows | `py -3 bludisko.py` |
| macOS alebo Linux | `python3 bludisko.py` |

Ak na svojom počítači spúšťaš Python 3 príkazom `python`, použi `python bludisko.py`.

## Ovládanie

| Čo chceš urobiť | Ako na to |
| --- | --- |
| Pohnúť sa o jedno políčko | Stlač šípku alebo klikni na políčko tesne vedľa líšky v jednom zo štyroch smerov. |
| Prejsť portálom | Vojdi na farebný kruh s písmenom. Stlač medzerník alebo klikni priamo na líšku. Prenesie sa na druhý koniec páru. |
| Nájsť cestu | Stlač **Nápoveda**. Zelený rámik ukáže ďalší krok najkratšej trasy. Ak máš použiť portál, pod mapou sa zobrazí pokyn. |
| Skúsiť tú istú mapu znova | Stlač **Od štartu**. Líška sa vráti na začiatok mapy a obe počítadlá sa vynulujú. |
| Vyskúšať inú mapu | Stlač **Nová mapa**. Hra vygeneruje iné bludisko na aktuálnej úrovni. |

## Úrovne a výsledok

Začínaš na mape s rozmermi 15 × 9 políčok. Posledný les má 37 × 21 políčok. V úrovniach 1–3 používaš pár **A**, v úrovniach 4–7 páry **A a B** a v úrovniach 8–10 všetky tri páry **A, B a C**. Portály fungujú oboma smermi.

Počítadlo pripočíta jeden krok za presun na voľné políčko aj za prechod portálom. Pri náraze do steny alebo mreže sa počet krokov nezmení. Pri lampáši sa zobrazí **„Vyhral si!“**, tvoj počet krokov a najmenší možný počet krokov pre túto mapu. Môžeš pokračovať na ďalšiu úroveň alebo hru ukončiť. Po desiatej úrovni môžeš hrať od začiatku s novými mapami.

## Udalosti a callbacky v Tkinteri

Callback je funkcia, ktorú Tkinter zavolá po udalosti. V triede `Hra` je pri každom callbacku komentár. Prvky `tk.Label` zobrazujú pokyny, úroveň, počet krokov a počet použitých párov portálov.

| Udalosť | Callback | Čo spraví |
| --- | --- | --- |
| Stlačenie klávesu v okne · `<KeyPress>` | `stlac_klaves` | Z `event.keysym` zistí, ktorú šípku hráč stlačil. |
| Ľavé kliknutie na mapu · `<Button-1>` | `klikni_na_mapu` | Prepočíta `event.x` a `event.y` z pixelov na políčko mriežky. |
| Medzerník na mape · `<space>` | `aktivuj_portal` | Prenesie líšku, ak stojí na portáli. |
| Zmena veľkosti plátna · `<Configure>` | `zmen_rozmery` | Prispôsobí veľkosť políčok a prekreslí mapu. |
| Tlačidlo **Nápoveda** | `ukaz_napovedu` | Vyznačí nasledujúci krok vrátane presunu portálom. |
| Tlačidlo **Od štartu** | `restartuj` | Začne nový pokus na rovnakej mape. |
| Tlačidlo **Nová mapa** | `nacitaj` | Prijme číslo aktuálnej úrovne cez `lambda` a vytvorí mapu. |
| Tlačidlo na pokračovanie po výhre | `pokracuj` | Načíta ďalšiu úroveň, po poslednej znova prvú. |

Klávesnicu a myš hra pripája cez `bind`, napríklad `okno.bind("<KeyPress>", self.stlac_klaves)`. Tlačidlo **Od štartu** používa `command=self.restartuj` bez zátvoriek. Pri tlačidle **Nová mapa** výraz `command=lambda: self.nacitaj(self.uroven)` odovzdá číslo úrovne až pri kliknutí.
