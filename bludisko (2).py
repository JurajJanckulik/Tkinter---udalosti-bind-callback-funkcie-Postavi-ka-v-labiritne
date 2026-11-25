"""Líška v bludisku – hra pre Python 3 s knižnicou tkinter."""

import random
import tkinter as tk
from collections import deque
from tkinter import font


# Názov úrovne a jej rozmery v políčkach. Nepárne rozmery nechávajú miesto stenám.
UROVNE = [
    ("Papraďový chodník", 15, 9),
    ("Borovicový háj", 19, 11),
    ("Hlboký les", 23, 13),
    ("Brezová húština", 25, 13),
    ("Tisová roklina", 27, 15),
    ("Jazvečia dolina", 29, 15),
    ("Hmlisté močiare", 31, 17),
    ("Soví vrch", 33, 17),
    ("Vlčia tiesňava", 35, 19),
    ("Les posledného lampáša", 37, 21),
]
SMERY = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
START = (1, 1)
PAPIER = "#f8f5eb"
ATRAMENT = "#183b30"
LES = "#244e40"
CESTA = "#e7e3c9"
ZLATO = "#ffc35a"
NAVOD = "Pohyb šípkami alebo kliknutím na susedné políčko."
# Písmeno, farba kameňa a farba svetelného kruhu každej dvojice.
PORTALY = [("A", "#164c64", "#76e5ef"), ("B", "#573269", "#f3b9fb"),
           ("C", "#793b24", "#ffca80")]
# S pribúdajúcimi portálmi sa farba lesa mení zo zelenej na hmlistú a súmračnú.
FARBY_LESA = [(LES, "#47705b"), ("#294c55", "#527981"), ("#393d56", "#666983")]


def vytvor_bludisko(sirka, vyska):
    """Vyhĺbi chodby medzi susednými políčkami, až kým nie sú všetky prepojené."""
    chodby = {START}
    zasobnik = [START]
    while zasobnik:
        x, y = zasobnik[-1]
        moznosti = []
        for dx, dy in SMERY.values():
            nx, ny = x + 2 * dx, y + 2 * dy
            if 0 < nx < sirka - 1 and 0 < ny < vyska - 1 and (nx, ny) not in chodby:
                moznosti.append((nx, ny))
        if not moznosti:
            zasobnik.pop()
            continue
        nx, ny = random.choice(moznosti)
        chodby.add(((x + nx) // 2, (y + ny) // 2))
        chodby.add((nx, ny))
        zasobnik.append((nx, ny))
    return chodby


def susedia(bod, chodby, spojenia=None):
    x, y = bod
    for dx, dy in SMERY.values():
        sused = (x + dx, y + dy)
        if sused in chodby:
            yield sused
    if spojenia and bod in spojenia:
        yield spojenia[bod]


def vzdialenosti_od(bod, chodby, spojenia=None):
    """Každý krok aj jeden presun portálom majú cenu jedného ťahu."""
    vzdialenost = {bod: 0}
    rad = deque([bod])
    while rad:
        teraz = rad.popleft()
        for sused in susedia(teraz, chodby, spojenia):
            if sused not in vzdialenost:
                vzdialenost[sused] = vzdialenost[teraz] + 1
                rad.append(sused)
    return vzdialenost


def rozmiestni_portaly(chodby, pocet):
    """Rozdelí jedinú cestu k lampášu mrežami a časti prepojí dvojicami portálov."""
    vzdialenost = vzdialenosti_od(START, chodby)
    ciel = max(vzdialenost, key=vzdialenost.get)
    cesta = [ciel]
    while cesta[-1] != START:
        bod = cesta[-1]
        cesta.append(min(susedia(bod, chodby), key=vzdialenost.get))
    cesta.reverse()

    # Nepárne indexy sú úzke priechody medzi miestnosťami. Ich uzavretím
    # vznikne presne o jednu oddelenú časť mapy viac za každú mrežu.
    rozostup = (len(cesta) - 1) // (pocet + 1)
    rezy = [2 * (i * rozostup // 2) + 1 for i in range(1, pocet + 1)]
    mreze = {cesta[i] for i in rezy}
    priechody = chodby - mreze
    spojenia = {}
    znacky = {}
    for cislo, rez in enumerate(rezy):
        konce = []
        for breh in (cesta[rez - 1], cesta[rez + 1]):
            okolie = vzdialenosti_od(breh, priechody)
            # Portály ukry v bočných uličkách, keď to tvar chodby umožňuje.
            dosah = max(1, min(8, rozostup // 3))
            miesta = [bod for bod, d in okolie.items() if 1 <= d <= dosah
                      and bod not in (START, ciel) and bod not in spojenia]
            slepe = [bod for bod in miesta if len(list(susedia(bod, priechody))) == 1]
            konce.append(random.choice(slepe or miesta))
        a, b = konce
        spojenia[a], spojenia[b] = b, a
        znacky[a] = znacky[b] = cislo
    return ciel, mreze, priechody, spojenia, znacky


class Hra:
    def __init__(self, okno):
        okno.title("Líška v bludisku")
        okno.configure(bg=PAPIER)
        okno.geometry("740x620")
        okno.minsize(490, 430)
        self.pismo = font.nametofont("TkDefaultFont").actual("family")

        hlavicka = tk.Frame(okno, bg=PAPIER)
        hlavicka.pack(fill="x", padx=20, pady=(14, 8))
        self.popis(hlavicka, "Líška v bludisku", 23, tucne=True).grid(sticky="w")
        self.popis(hlavicka, "Obíď mreže cez portály a nájdi zlatý lampáš.", 11).grid(
            row=1, column=0, columnspan=2, sticky="w")
        hlavicka.columnconfigure(0, weight=1)
        self.krokomer = self.popis(hlavicka, "", 16, tucne=True)
        self.krokomer.grid(row=0, column=1, sticky="e")

        info = tk.Frame(okno, bg=PAPIER)
        info.pack(fill="x", padx=20, pady=(4, 5))
        self.oznacenie = self.popis(info, "", 11, tucne=True)
        self.oznacenie.pack(side="left")
        self.pocitadlo_portalov = self.popis(info, "", 10)
        self.pocitadlo_portalov.pack(side="right")
        self.platno = tk.Canvas(okno, width=600, height=330, bg=ATRAMENT,
                               highlightthickness=0, bd=0)
        self.platno.pack(fill="both", expand=True, padx=20)

        self.ovladanie = tk.Frame(okno, bg=PAPIER)
        self.stav = self.popis(self.ovladanie, "", 11)
        self.stav.pack(anchor="w", pady=(0, 4))
        panel = tk.Frame(self.ovladanie, bg=PAPIER)
        panel.pack(fill="x")
        for stlpec in range(3):
            panel.columnconfigure(stlpec, weight=1, uniform="tlacidla")

        # command dostáva názov metódy bez zátvoriek. Tk ju zavolá až pri stlačení.
        self.tlacidlo(panel, "Nápoveda", command=self.ukaz_napovedu).grid(
            row=0, column=0, sticky="ew", padx=(0, 3))
        self.tlacidlo(panel, "Od štartu", command=self.restartuj).grid(
            row=0, column=1, sticky="ew", padx=3)
        # Kliknutie na Novú mapu odovzdá cez lambda číslo aktuálnej úrovne.
        self.tlacidlo(panel, "Nová mapa", command=lambda: self.nacitaj(self.uroven)).grid(
            row=0, column=2, sticky="ew", padx=(3, 0))

        self.vysledok = tk.Frame(okno, bg=PAPIER)
        self.popis(self.vysledok, "Vyhral si!", 20, tucne=True).pack(anchor="w")
        self.suhrn = self.popis(self.vysledok, "", 11)
        self.suhrn.pack(anchor="w", pady=(1, 8))
        volby = tk.Frame(self.vysledok, bg=PAPIER)
        volby.pack(fill="x")
        self.dalej = self.tlacidlo(volby, "", command=self.pokracuj)
        self.dalej.pack(side="left", fill="x", expand=True, padx=(0, 4))
        # Kliknutie na Ukončiť hru zavrie hlavné okno aj celú aplikáciu.
        self.tlacidlo(volby, "Ukončiť hru", command=okno.destroy).pack(
            side="left", fill="x", expand=True, padx=(4, 0))

        self.policko = 1
        self.okraj_x = self.okraj_y = 0
        self.nacitaj(0)
        okno.bind("<KeyPress>", self.stlac_klaves)
        self.platno.bind("<Button-1>", self.klikni_na_mapu)
        self.platno.bind("<space>", self.aktivuj_portal)
        self.platno.bind("<Configure>", self.zmen_rozmery)
        self.platno.focus_set()

    def popis(self, rodic, text, velkost, tucne=False):
        styl = "bold" if tucne else "normal"
        return tk.Label(rodic, text=text, bg=PAPIER, fg=ATRAMENT, bd=0,
                        anchor="w", font=(self.pismo, velkost, styl))

    def tlacidlo(self, rodic, text, command):
        return tk.Button(rodic, text=text, command=command, bg=LES, fg="white",
                         activebackground="#365f4d", activeforeground="white",
                         disabledforeground="#a6b8a9", font=(self.pismo, 10),
                         bd=0, highlightthickness=1, highlightbackground=PAPIER,
                         highlightcolor="#bb762b", padx=3, pady=6)

    # Callback pre tlačidlo Nová mapa. Parameter cez lambda určuje úroveň mapy.
    def nacitaj(self, cislo):
        self.uroven = cislo
        nazov, self.sirka, self.vyska = UROVNE[cislo]
        mapa = vytvor_bludisko(self.sirka, self.vyska)
        # Úrovne 1–3 používajú pár A, 4–7 páry A/B a 8–10 páry A/B/C.
        self.pocet_parov = 1 + (cislo >= 3) + (cislo >= 7)
        (self.ciel, self.mreze, self.chodby, self.spojenia,
         self.znacky) = rozmiestni_portaly(mapa, self.pocet_parov)
        self.do_ciela = vzdialenosti_od(self.ciel, self.chodby, self.spojenia)
        self.oznacenie.config(text=f"Úroveň {cislo + 1} / {len(UROVNE)}   ·   {nazov}")
        self.zacni_pokus()
        self.vykresli_mapu()

    def zacni_pokus(self):
        self.poloha = START
        self.kroky = 0
        self.napoveda = None
        self.pouzite_pary = set()
        self.aktualizuj_pocitadlo_portalov()
        self.krokomer.config(text="Kroky: 0")
        self.stav.config(text=NAVOD)
        self.vysledok.pack_forget()
        self.ovladanie.pack(side="bottom", before=self.platno, fill="x", padx=20, pady=(8, 12))

    # Callback pre tlačidlo Od štartu. Ponechá rovnaké bludisko.
    def restartuj(self):
        self.zacni_pokus()
        self.vykresli_postavy()
        self.platno.focus_set()

    # Callback pre tlačidlo Pokračovať alebo Hrať od začiatku po výhre.
    def pokracuj(self):
        if self.poloha == self.ciel:
            self.nacitaj((self.uroven + 1) % len(UROVNE))
            self.platno.focus_set()

    # Callback pre stlačenie klávesu v okne. Podľa event.keysym vyberie smer.
    def stlac_klaves(self, event):
        if event.keysym in SMERY:
            if self.poloha != self.ciel:
                self.platno.focus_set()
            self.posun(*SMERY[event.keysym])
            return "break"

    # Callback pre ľavé kliknutie na plátno. Prepočíta event.x a event.y na políčko.
    def klikni_na_mapu(self, event):
        self.platno.focus_set()
        x = (event.x - self.okraj_x) // self.policko
        y = (event.y - self.okraj_y) // self.policko
        if not (0 <= x < self.sirka and 0 <= y < self.vyska) or self.poloha == self.ciel:
            return
        dx, dy = x - self.poloha[0], y - self.poloha[1]
        if (x, y) == self.poloha and self.poloha in self.spojenia:
            self.aktivuj_portal()
        elif abs(dx) + abs(dy) == 1:
            self.posun(dx, dy)
        else:
            self.stav.config(text="Klikni na políčko hneď vedľa líšky.")

    # Callback pre tlačidlo Nápoveda. Vyznačí jeden krok po najkratšej ceste.
    def ukaz_napovedu(self):
        if self.poloha == self.ciel:
            return
        self.napoveda = min(susedia(self.poloha, self.chodby, self.spojenia),
                            key=self.do_ciela.get)
        if self.napoveda == self.spojenia.get(self.poloha):
            self.stav.config(text="Prejdi portálom: stlač medzerník alebo klikni na líšku.")
        else:
            self.stav.config(text="Posuň sa na políčko so zeleným rámikom.")
        self.platno.focus_set()
        self.vykresli_postavy()

    def aktualizuj_pocitadlo_portalov(self):
        self.pocitadlo_portalov.config(text=f"Použité páry: {len(self.pouzite_pary)} / {self.pocet_parov}")

    # Callback pre medzerník na mape alebo kliknutie na líšku stojacu v portáli.
    def aktivuj_portal(self, event=None):
        if self.poloha in self.spojenia:
            odkial = self.poloha
            cislo = self.znacky[self.poloha]
            self.pouzite_pary.add(cislo)
            self.aktualizuj_pocitadlo_portalov()
            self.dokonci_krok(self.spojenia[self.poloha])
            # Svetelná stopa na oboch koncoch ukáže smer aj pri dlhom presune.
            for bod in (odkial, self.poloha):
                x = self.okraj_x + bod[0] * self.policko
                y = self.okraj_y + bod[1] * self.policko
                for okraj, trvanie in ((0.04, 180), (0.13, 320)):
                    d = self.policko * okraj
                    kruh = self.platno.create_oval(x+d, y+d, x+self.policko-d, y+self.policko-d,
                                                  outline=PORTALY[cislo][2], width=2, tags="zablesk")
                    self.platno.after(trvanie, self.platno.delete, kruh)
            pismeno = PORTALY[cislo][0]
            self.stav.config(text=f"Portál {pismeno} ťa preniesol. Pokračuj po chodníku.")
        return "break"

    def posun(self, dx, dy):
        if self.poloha == self.ciel:
            return
        x, y = self.poloha
        nova = (x + dx, y + dy)
        if nova in self.mreze:
            self.stav.config(text="Mreža je zamknutá. Nájdi farebný portál.")
            return
        if nova not in self.chodby:
            self.stav.config(text="Tu rastie les. Skús inú cestu.")
            return
        self.dokonci_krok(nova)

    def dokonci_krok(self, nova):
        self.poloha = nova
        self.kroky += 1
        self.napoveda = None
        self.krokomer.config(text=f"Kroky: {self.kroky}")
        if nova == self.ciel:
            self.zobraz_vyhru()
        elif nova in self.spojenia:
            pismeno = PORTALY[self.znacky[nova]][0]
            self.stav.config(text=f"Portál {pismeno}: stlač medzerník alebo klikni na líšku.")
        else:
            self.stav.config(text=NAVOD)
        self.vykresli_postavy()

    def zobraz_vyhru(self):
        if self.uroven + 1 < len(UROVNE):
            sprava = "Našiel si lampáš."
            volba = f"Pokračovať na {self.uroven + 2}. úroveň"
        else:
            sprava = "Našiel si aj posledný lampáš!"
            volba = "Hrať od začiatku"
        self.suhrn.config(text=f"{sprava}   Kroky: {self.kroky}   ·   Minimum: {self.do_ciela[START]}")
        self.dalej.config(text=volba)
        self.ovladanie.pack_forget()
        self.vysledok.pack(side="bottom", before=self.platno, fill="x", padx=20, pady=(8, 12))
        self.dalej.focus_set()

    # Callback pre zmenu veľkosti plátna. Prispôsobí mapu rozmerom okna.
    def zmen_rozmery(self, event):
        self.vykresli_mapu()

    def vykresli_mapu(self):
        p = self.platno
        w, h = p.winfo_width(), p.winfo_height()
        s = max(1, min((w - 16) // self.sirka, (h - 16) // self.vyska))
        self.policko = s
        self.okraj_x = (w - self.sirka * s) // 2
        self.okraj_y = (h - self.vyska * s) // 2
        x0, y0 = self.okraj_x, self.okraj_y
        les, ihlicie = FARBY_LESA[self.pocet_parov - 1]
        p.delete("all")
        p.create_rectangle(x0, y0, x0 + self.sirka * s, y0 + self.vyska * s,
                           fill=les, width=0)
        for y in range(self.vyska):
            for x in range(self.sirka):
                x1, y1 = x0 + x * s, y0 + y * s
                if (x, y) in self.chodby:
                    p.create_rectangle(x1, y1, x1 + s, y1 + s, fill=CESTA, width=0)
                    p.create_line(x1, y1 + s - 1, x1, y1, x1 + s - 1, y1, fill="#d2d1b6")
                    if (x, y) in self.znacky:
                        pismeno, kamen, ziara = PORTALY[self.znacky[(x, y)]]
                        p.create_oval(x1 + .05*s, y1 + .05*s, x1 + .95*s, y1 + .95*s,
                                      fill=kamen, outline=ziara, width=max(1, s//12))
                        p.create_oval(x1 + .20*s, y1 + .20*s, x1 + .80*s, y1 + .80*s,
                                      outline=ziara, width=1)
                        p.create_text(x1 + .50*s, y1 + .50*s, text=pismeno,
                                      fill="white", font=(self.pismo, -max(6, s//2), "bold"))
                elif (x, y) in self.mreze:
                    p.create_rectangle(x1, y1, x1+s, y1+s, fill="#3d3630", width=0)
                    for diel in (.24, .50, .76):
                        p.create_line(x1+diel*s, y1+.08*s, x1+diel*s, y1+.92*s,
                                      fill="#deb781", width=max(1, s//11))
                    p.create_line(x1+.04*s, y1+.54*s, x1+.96*s, y1+.54*s,
                                  fill="#ac8257", width=max(1, s//8))
                elif (x + 3 * y) % 4 == 0:
                    # Dve vetvičky značia ihličnatý strom na nepriechodnom políčku.
                    for posun in (0.0, 0.13):
                        p.create_line(x1 + 0.32 * s, y1 + (0.56 + posun) * s,
                                      x1 + 0.50 * s, y1 + (0.34 + posun) * s,
                                      x1 + 0.68 * s, y1 + (0.56 + posun) * s,
                                      fill=ihlicie, width=max(1, s // 20))
        self.vykresli_postavy()

    def vykresli_postavy(self):
        p, s = self.platno, self.policko
        p.delete("figurky")

        # Obrázky sa kreslia priamo v políčku, hra nepotrebuje externé súbory.
        def tvar(bod, farba, vrcholy, zrkadlit=False):
            x = self.okraj_x + bod[0] * s
            y = self.okraj_y + bod[1] * s
            if zrkadlit:
                vrcholy = [(1 - a, b) for a, b in vrcholy]
            suradnice = [(x + a * s, y + b * s) for a, b in vrcholy]
            p.create_polygon(suradnice, fill=farba, outline="", tags="figurky")

        if self.napoveda is not None:
            x = self.okraj_x + self.napoveda[0] * s
            y = self.okraj_y + self.napoveda[1] * s
            p.create_rectangle(x+.05*s, y+.05*s, x+.95*s, y+.95*s,
                               outline="#15704e", width=max(2, s//10), tags="figurky")
        # Zlaté sklo, tmavý rám a rúčka lampáša.
        tvar(self.ciel, "#704c23", [(.36, .28), (.43, .12), (.57, .12), (.64, .28),
                                    (.78, .36), (.69, .81), (.74, .88), (.26, .88), (.31, .81), (.22, .36)])
        tvar(self.ciel, ZLATO, [(.33, .4), (.67, .4), (.6, .73), (.4, .73)])
        tvar(self.ciel, "#fff9d4", [(.5, .44), (.58, .59), (.5, .69), (.42, .59)])

        # Silueta líšky, vnútorné uši, biele líca, oči a ňufák.
        tvar(self.poloha, "#994722", [(.09, .08), (.39, .23), (.61, .23), (.91, .08),
                                     (.86, .58), (.75, .76), (.5, .95), (.25, .76), (.14, .58)])
        tvar(self.poloha, "#ec7b36", [(.16, .15), (.4, .31), (.6, .31), (.84, .15),
                                     (.79, .58), (.68, .72), (.5, .87), (.32, .72), (.21, .58)])
        for zrkadlit in (False, True):
            tvar(self.poloha, "#643f32", [(.18, .19), (.33, .29), (.21, .38)], zrkadlit)
            tvar(self.poloha, "#fff1ce", [(.16, .58), (.37, .64), (.5, .8), (.5, .9), (.26, .74)], zrkadlit)
            tvar(self.poloha, "#29372e", [(.28, .49), (.37, .51), (.37, .58), (.29, .57)], zrkadlit)
        tvar(self.poloha, "#29372e", [(.42, .78), (.58, .78), (.5, .88)])


if __name__ == "__main__":
    okno = tk.Tk()
    hra = Hra(okno)
    okno.mainloop()
