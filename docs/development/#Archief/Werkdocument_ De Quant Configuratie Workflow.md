# **Werkdocument: De Quant Configuratie Workflow**

Versie: 1.0  
Status: Levend Document  
Dit document schetst de "top-down" configuratie-workflow voor de kwantitatieve analist (de "quant"). Het beschrijft de gebruikersreis van het opzetten van een portfolio tot het configureren van een specifieke, context-bewuste strategie. Deze workflow is de blauwdruk voor de gebruikersinterface (UI) en de interactie met de backend.

## **Overzicht: Een Gelaagde Configuratie**

De filosofie is dat de configuratie in lagen gebeurt. Elke laag bouwt voort op de vorige, waardoor de keuzes voor de gebruiker steeds relevanter en specifieker worden. De hiërarchie is als volgt:

**Portfolio → Strategie → Plugins**

## **Fase 1: De Portfolio Configuratie (Het Fundament)**

Alles begint met het definiëren van het **Portfolio**. Dit is de "wereld" waarin een strategie zal opereren. Het definieert de omgeving, de beschikbare middelen (data, kapitaal) en de overkoepelende regels.

* **Doel**: De volledige context voor alle toekomstige strategie-runs vastleggen.  
* **Resultaat**: Een opgeslagen configuratie (bv. mijn\_portfolio.yaml), gevalideerd door een portfolio\_schema.py.

### **UI-Interactie: De Portfolio Wizard**

De gebruiker wordt door een wizard geleid om zijn portfolio te configureren.

1. **Selecteer Omgeving (type)**: De eerste en belangrijkste keuze, die de rest van de opties bepaalt.  
   * Backtest: Gebruikt historische data.  
   * Paper Trading: Simuleert live trading op een live datafeed.  
   * Live Trading: Voert daadwerkelijk trades uit op een live datafeed.  
2. **Definieer Data Bron(nen)**: Op basis van de gekozen omgeving:  
   * **Voor Live / Paper**: Een dropdown-menu toont de beschikbare, voorgeconfigureerde connector\_id's uit connectors.yaml. Na selectie (bv. kraken\_public), haalt de UI op de achtergrond de beschikbare datastromen voor die connector op.  
   * **Voor Backtest**: Een multi-select lijst toont de beschikbare, lokaal opgeslagen data-archieven (bv. kraken\_public/BTC\_EUR/trades).  
3. **Stel Kapitaal & Risico in**: Velden voor startkapitaal, standaard risicopercentage per trade, maximale portfolio drawdown, etc.  
4. **Activeer Portfolio Specialisten**: Een set van "bots" op portfolio-niveau die *naast* de strategie draaien. De gebruiker kan deze hier aan- of uitzetten:  
   * GridTraderAgent  
   * DCAAgent  
   * RebalancerAgent

## **Fase 2: De Strategie Configuratie (Context-Bewust Bouwen)**

De gebruiker start de "Nieuwe Strategie Wizard" **vanuit een specifiek, geconfigureerd portfolio**. De wizard is nu "slim" en gebruikt de portfolio-context om de gebruiker te helpen.

* **Doel**: De specifieke handelslogica (de 9-fasen pijplijn) definiëren.  
* **Resultaat**: Een opgeslagen strategie-configuratie (bv. mijn\_fvg\_strategie.yaml).

### **UI-Interactie: De Strategie Wizard**

1. **Selecteer Data**:  
   * De dropdown voor het **handelspaar** toont alleen de paren die beschikbaar zijn binnen het geselecteerde portfolio.  
   * De gebruiker selecteert het **executie-timeframe** (bv. 15m of ticks). Dit wordt de "hartslag" van de StrategyEngine.  
2. **Bouw de Pijplijn (De "Slimme" LEGO-doos)**:  
   * De gebruiker ziet de visuele 9-fasen pijplijn en een bibliotheek met alle beschikbare plugins. Deze bibliotheek wordt **dynamisch gefilterd** op basis van de portfolio-context:  
   * **Vereiste Data (requires\_context)**: Een plugin die orderboek-data *vereist* (OrderbookImbalanceRefiner), wordt **grijs weergegeven en is niet selecteerbaar** als het portfolio geen live orderboek-stream heeft geconfigureerd. Een tooltip legt uit waarom.  
   * **Optionele Data (uses)**: Een plugin die *optioneel* tick-data gebruikt voor extra precisie, is **wel selecteerbaar** maar krijgt een **waarschuwingsicoon (⚠️)**. Een tooltip legt uit: "Deze plugin zal in een beperkte modus werken op basis van candle-data, omdat er geen tick-stream beschikbaar is."  
   * **Timeframe Management**: Een plugin heeft 1h data nodig, maar het executie-timeframe is 15m. De wizard detecteert dit en vraagt:  
     * "Deze plugin vereist 1-uur data. Wilt u deze:"  
     * **Optie A**: "Vooraf genereren en opslaan in het archief?" (Aanbevolen voor backtests)  
     * **Optie B**: "On-the-fly berekenen tijdens de run?" (Flexibeler voor live)

### **Conclusie: Een Gelaagde Verantwoordelijkheid**

Deze workflow formaliseert de scheiding van zorgen en creëert een intuïtieve gebruikerservaring:

* **Het Portfolio** definieert de **wereld** (de omgeving en beschikbare middelen).  
* **De Strategie** definieert de **logica** die binnen die wereld opereert.  
* **De UI Wizard** fungeert als een **intelligente assistent** die de regels en middelen van de "wereld" (het portfolio) kent en de quant helpt om een logica (strategie) te bouwen die daarbinnen kan functioneren.

De strategie *code* blijft agnostisch, maar de *configuratie-ervaring* is dat terecht **niet**.