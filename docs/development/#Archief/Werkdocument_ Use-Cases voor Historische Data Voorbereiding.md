# **Werkdocument: Use-Cases voor Historische Data Voorbereiding**

Versie: 1.0  
Status: Levend Document  
Dit document beschrijft de gebruikersinteracties (use-cases) voor de "Historische data voorbereiding"-flow binnen het backtest-dashboard. Het dient als leidraad voor de ontwikkeling van de UI en de bijbehorende backend-services, met de (crypto) quant als primaire gebruiker.

## **1\. Flow: Data Acquisitie (Een Nieuw Archief Aanmaken)**

Deze flow beschrijft de wizard waarmee een gebruiker een nieuw historisch data-archief voor een specifiek handelspaar aanmaakt.

### **1.1. Gebruikersinteractie: De Wizard**

De wizard leidt de gebruiker door de volgende stappen:

1. **Selecteer de Data Bron**: Dit is het eerste en belangrijkste keuzecriterium. De gebruiker kiest waar de data vandaan moet komen. De UI presenteert dit als begrijpelijke categorieën:  
   * **Live Exchange Verbinding**: Een dropdown-menu met de logische namen van de verbindingen die in connectors.yaml zijn geconfigureerd (bv. kraken\_public, binance\_private).  
     * *Technische vertaling*: De geselecteerde naam wordt de connector\_id in de DTO.  
   * **Lokaal Data-Archief**: Een optie om data te gebruiken die al lokaal is opgeslagen.  
     * *Technische vertaling*: Dit correspondeert met een interne, speciale connector\_id zoals 'local\_archive\_connector'.  
   * **Importeer CSV-Bestand**: Een upload-knop om een lokaal bestand te selecteren.  
     * *Technische vertaling*: Dit correspondeert met een interne connector\_id zoals 'csv\_import\_connector'.  
2. **Selecteer Handelspaar & Timeframe**: Op basis van de gekozen bron toont de UI een lijst met beschikbare handelsparen en timeframes.  
3. **Definieer de Periode**: De gebruiker geeft een startdatum op om de historische data op te halen.  
4. **Start de Download**: Een knop om het proces te starten, wat de DataCommandService.fetch\_period methode aanroept. De UI toont de voortgang.

## **2\. Flow: Data Onderhoud & Beheer**

Deze flow beschrijft de interacties vanuit een centraal dashboard dat een overzicht geeft van alle lokaal opgeslagen data-archieven.

### **2.1. Gebruikersinteractie: Het Data Overzicht**

Het dashboard toont een tabel met alle beschikbare data-archieven. Deze tabel moet de volgende functionaliteit bieden:

* **Kolommen**: Bron (connector\_id), Handelspaar, Timeframe, Begin Datum, Eind Datum, Omvang (MB), Compleetheid (%), Aantal Gaten.  
* **Sorteren & Filteren**: De gebruiker moet kunnen sorteren en filteren op al deze kolommen, met name op "Bron" om snel alle data van een specifieke exchange te zien.

### **2.2. Gebruikersinteractie: Acties per Archief**

Voor elk archief in de lijst zijn de volgende onderhoudsacties beschikbaar (bv. via een contextmenu):

* **Synchroniseren**: Werkt het archief bij met de allerlaatste data tot nu. Roept DataCommandService.synchronize aan.  
* **Historie Vergroten**: Breidt het archief verder uit terug in de tijd. Roept DataCommandService.extend\_history aan.  
* **Gaten Vullen**: Detecteert en downloadt ontbrekende data binnen de bestaande periode. Roept DataCommandService.fill\_gaps aan.  
* **Comprimeren (Compaction)**: Optimaliseert de opslag door de vele kleine download-bestandjes samen te voegen tot grotere, performante bestanden (bv. één bestand per dag of maand). Dit verbetert de leessnelheid voor backtests aanzienlijk.

## **3\. Flow: Quant-Centric Features (Vertrouwen & Flexibiliteit)**

Dit zijn geavanceerde features die essentieel zijn voor de professionele workflow van een quant.

### **3.1. Use-Case: Data Inspectie & Validatie**

* **Gebruikersdoel**: Snel en visueel vertrouwen krijgen in de kwaliteit van een data-archief voordat een tijdrovende backtest wordt gestart.  
* **UI-interactie**: Een "Inspecteer" knop per archief in het overzicht.  
* **Functionaliteit**: Opent een scherm met:  
  1. **Candlestick-grafiek**: Voor een snelle visuele inspectie op uitschieters, gaten of verdachte patronen.  
  2. **Basisstatistieken**: Een overzicht met o.a. het aantal datapunten, begin/eindtijd, hoogste/laagste prijs, en informatie over het grootste gedetecteerde gat.

### **3.2. Use-Case: Resampling naar Andere Timeframes**

* **Gebruikersdoel**: Een strategie eenvoudig testen op meerdere timeframes zonder handmatig data te moeten manipuleren.  
* **UI-interactie**: Een "Genereer Timeframe" actie in het onderhoudsmenu.  
* **Functionaliteit**: Een wizard die de gebruiker toestaat om vanuit een bron-archief (bv. 1-minuut data) een compleet nieuw, afgeleid archief te genereren voor een hoger timeframe (bv. 15-minuten of 4-uur data).

### **3.3. Use-Case: Bronbeheer & Herkomst (Architectuur)**

* **Gebruikersdoel**: Strategieën testen en vergelijken over meerdere exchanges (bv. voor arbitrage of robuustheidstests).  
* **Architectonische Vereiste**: De opslagstructuur van de data moet de bron (connector\_id) als een primair onderdeel bevatten.  
  * **Voorgestelde Structuur**: source\_data/{connector\_id}/{pair}/{timeframe}/...  
  * **Voorbeeld**:  
    * source\_data/kraken\_public/BTC\_EUR/15m/  
    * source\_data/binance\_public/BTC\_EUR/15m/  
* **Impact**: Dit is een fundamentele keuze die het mogelijk maakt om data voor hetzelfde paar van verschillende bronnen gescheiden te houden, wat essentieel is voor geavanceerde kwantitatieve analyses.