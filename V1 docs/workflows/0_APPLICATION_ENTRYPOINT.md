# 0. Applicatie Entrypoint en Flow

Dit document beschrijft de opstart-workflow van de S1mpleTrader applicatie, die wordt beheerd door `main.py`. Dit bestand fungeert als de enige "voordeur" van de applicatie en stuurt de gebruiker door op basis van de meegegeven argumenten.

## 0.1. De Analogie: De Receptie

`main.py` werkt als de receptie van een bedrijf:
* **Bezoeker met afspraak (Directe Aanroep):** Als een gebruiker de applicatie start met command-line argumenten (bv. `--run mss_base --mode backtester`), weet de receptionist precies waar de bezoeker naartoe moet. De gebruiker wordt direct naar de juiste afdeling (`BacktesterApp`) gestuurd.
* **Bezoeker zonder afspraak (Interactieve Menu):** Als een gebruiker de applicatie start zonder argumenten (`python main.py`), weet de receptionist niet wat de bedoeling is. De gebruiker wordt naar de wachtkamer met een keuzemenu (`MainMenuPresenter`) gestuurd om zelf aan te geven wat hij wil doen.

## 0.2. De Twee Paden

De applicatie kent twee opstartpaden, die worden bepaald door de aan- of afwezigheid van command-line argumenten.

### **Pad 1: Directe Aanroep**
```
Gebruiker: python main.py --run mss_base --mode backtester --override use_eth

  │
  ▼

1. main.py:
   - `argparse` leest de argumenten (`run`, `mode`, `override`).
   - Detecteert dat argumenten aanwezig zijn.

  │
  ▼

2. run_cli(run_name, mode_name, override_name):
   - De `mode_name` ('backtester') wordt gebruikt als `app_name`.
   - De juiste app controller (`BacktesterApp`) wordt gestart.

  │
  ▼

3. BacktesterApp:
   - De backtest wordt direct uitgevoerd met de opgegeven configuratie.
```

### **Pad 2: Interactieve Menu**
```
Gebruiker: python main.py

  │
  ▼

1. main.py:
   - `argparse` leest de argumenten.
   - Detecteert dat er geen argumenten zijn meegegeven.
   - Stelt `app_name` in op 'main_menu'.

  │
  ▼

2. run_cli(app_name='main_menu'):
   - De `MainMenuPresenter` wordt gestart.

  │
  ▼

3. MainMenuPresenter:
   - Toont het interactieve hoofdmenu, van waaruit de gebruiker
     vervolgens een backtest, optimalisatie, etc. kan starten.
```