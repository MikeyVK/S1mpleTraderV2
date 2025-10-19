# **Addendum: 5.1 Impact van de "Point-in-Time" Architectuur**

Dit addendum beschrijft de fundamentele impact van de overstap naar de "Point-in-Time" (v2) architectuur op het gehele S1mpleTrader systeemontwerp. Deze nieuwe filosofie, gericht op een live-first mentaliteit en expliciete, atomaire data-uitwisseling, vervangt het concept van de enriched\_df en heeft significante gevolgen voor de bestaande documentatie.

## **1\. Impact op Bestaande Documentatie**

De "Point-in-Time" architectuur is een paradigmaverschuiving. De volgende secties en concepten in de oorspronkelijke documentatie (docs.md) zijn door dit addendum achterhaald of vereisen een significant andere interpretatie.

### **Hoofdstuk 2: 2\_ARCHITECTURE.md**

* **Paragraaf 2.4. Het Worker Ecosysteem & 2.11. Dataflow & Orchestratie**:  
  * **Verouderd:** De beschrijving van de dataflow waarbij ContextWorkers een TradingContext verrijken door direct een enriched\_df te muteren.  
  * **Nieuw:** De dataflow is nu DTO-gedreven. ContextWorkers produceren ContextUpdateDTO's. De ContextOperator is verantwoordelijk voor het *integreren* van deze DTOs in het TradingContext-object. OpportunityWorkers en andere consumenten lezen uit het computed\_values object, niet uit een enriched\_df.

### **Hoofdstuk 4: 4\_DE\_PLUGIN\_ANATOMIE.md**

* **Paragraaf 4.3.2. Dependencies (Het Data Contract)**:  
  * **Verouderd:** De betekenis van requires en provides als pure DataFrame kolomnamen is te beperkt.  
  * **Nieuw:** De dependencies sectie in manifest.yaml wordt veel explicieter:  
    * requires\_environment\_data: Declareert de behoefte aan "ruwe" data (ohlcv\_df, current\_price).  
    * requires\_computed\_keys: Declareert de behoefte aan specifieke, berekende datapunten.  
    * produces\_dto & produces\_keys: Declareert de DTO die de worker retourneert en de datapunten die het produceert.

### **Hoofdstuk 5: 5\_DE\_WORKFLOW\_ORKESTRATIE.md**

* **Alle Paragrafen:** De gehele beschrijving van de workflow, hoewel de 5 fases (Context, Opportunity, etc.) overeind blijven, moet worden herlezen met het DTO-gedreven, punt-in-tijd model in gedachten.  
  * **Verouderd:** De aanname dat workers opereren op een gedeeld, verrijkt DataFrame.  
  * **Nieuw:** Workers opereren op een minimalistische TradingContext en wisselen data uit via expliciete DTOs. Workers die historische *berekende* waarden nodig hebben (voor 'crosses' e.d.), zijn nu zelf verantwoordelijk voor het bijhouden van hun staat via de state capability.

### **Addendum 11\_6.7 dependency\_validator.md**

* **Verouderd:** De implementatie die zich richt op het valideren van DataFrame kolomnamen (available\_columns).  
* **Nieuw:** De DependencyValidator krijgt een veel geavanceerdere en crucialere rol. Het moet de volledige keten van produces\_keys en requires\_computed\_keys door de sequentiële ContextWorker-pijplijn heen valideren om te garanderen dat alle data-afhankelijkheden zijn voldaan voordat een run start.

## **2\. De "Point-in-Time" Architectuur in Detail**

### **2.1. Kerninzicht & Probleemstelling**

Het concept van een enriched\_df is een overblijfsel van een backtest-first, batch-processing mentaliteit. Een live-omgeving (en dus ook een gesimuleerde live-omgeving zoals backtesting) opereert op basis van **discrete momentopnames ("Point-in-Time")**. De TradingContext moet deze realiteit weerspiegelen en mag geen "vergaarbak" zijn van data die een worker *mogelijk* nodig heeft.

### **2.2. Het Nieuwe Paradigma: Atomaire, Expliciete Context**

De principes worden aangescherpt voor maximale explicietheid en single responsibility:

* **Minimale TradingContext:** De TradingContext die door de ExecutionEnvironment wordt geproduceerd, bevat alleen de absolute basis: timestamp, asset\_pair.  
* **Expliciete Data-Afhankelijkheid:** Een worker **moet** in zijn manifest.yaml expliciet declareren welke data hij nodig heeft, inclusief basisdata zoals ohlcv\_df of current\_price. De ContextOperator levert alleen de data die is aangevraagd.  
* **Workers als Pure Functies:** Een ContextWorker ontvangt een TradingContext met alleen de data die hij nodig heeft, berekent een **enkel, punt-in-tijd datapunt**, en retourneert dit in een ContextUpdateDTO.  
* **Operator als Integrator:** De ContextOperator bouwt de TradingContext stapsgewijs op door DTO-outputs te mergen.  
* **Worker is Verantwoordelijk voor Eigen Geschiedenis:** Een worker die historische *berekende* waarden nodig heeft (bv. voor het detecteren van een 'cross'), is zelf verantwoordelijk voor het bijhouden van zijn vorige staat. Het platform faciliteert dit via de **state capability**, maar pusht geen previous\_computed\_values meer.

### **2.3. De Herziene Componenten**

#### **2.3.1. Het TradingContext DTO (Ultra-Minimalistisch)**

De TradingContext is nu een nog minimalistischere container. Het veld previous\_computed\_values is **verwijderd**.

from pydantic import BaseModel, Field  
from typing import Dict, Any, Optional  
import pandas as pd  
from datetime import datetime

class ComputedValues(BaseModel):  
    """Gestructureerde container voor alle berekende 'point-in-time' waarden."""  
    indicators: Dict\[str, float | int | bool\] \= Field(default\_factory=dict)  
    structure: Dict\[str, float | int | bool | str\] \= Field(default\_factory=dict)  
    regime: Dict\[str, float | int | bool | str\] \= Field(default\_factory=dict)

class TradingContext(BaseModel):  
    """De staat van de wereld op tijdstip T."""  
    timestamp: datetime  
    asset\_pair: str  
      
    \# Data wordt alleen gevuld als een worker erom vraagt in zijn manifest  
    current\_price: Optional\[float\] \= None  
    ohlcv\_df: Optional\[pd.DataFrame\] \= None  
      
    \# De container voor berekende waarden  
    computed\_values: ComputedValues \= Field(default\_factory=ComputedValues)

    class Config:  
        arbitrary\_types\_allowed \= True

#### **2.3.2. De ContextWorker Workflow (Ongewijzigd)**

De output van een ContextWorker blijft een ContextUpdateDTO.

\# Voorbeeld: EMADetector  
def process(self, context: TradingContext) \-\> ContextUpdateDTO:  
    \# Worker vertrouwt erop dat ohlcv\_df aanwezig is, omdat dit in zijn manifest staat  
    ema\_series \= context.ohlcv\_df\['close'\].ewm(span=20).mean()  
    current\_ema\_value \= ema\_series.iloc\[-1\]  
      
    return ContextUpdateDTO(  
        source\_plugin="ema\_detector",  
        data={"indicator.ema.20": current\_ema\_value}  
    )

#### **2.3.3. De Consument (OpportunityWorker) met state Capability**

Een worker die de vorige staat van een berekende waarde nodig heeft, gebruikt zijn eigen, persistente state.

\# Voorbeeld: EMACrossOpportunity worker.py

class EMACrossOpportunity(StandardWorker):  
    \# Deze worker heeft de 'state' capability aangevraagd in zijn manifest.  
    \# 'self.state' en 'self.commit\_state()' worden geïnjecteerd.  
      
    def process(self, context: TradingContext) \-\> List\[Signal\]:  
        \# Haal huidige waarde op uit de context  
        current\_ema\_fast \= context.computed\_values.indicators.get("indicator.ema.20")  
          
        \# Haal vorige waarde op uit de EIGEN state  
        prev\_ema\_fast \= self.state.get("last\_ema\_20")  
          
        \# Sla de huidige waarde op voor de VOLGENDE tick  
        self.state\["last\_ema\_20"\] \= current\_ema\_fast  
          
        if prev\_ema\_fast is None or current\_ema\_fast is None:  
            self.commit\_state() \# Sla staat toch op  
            return \[\] \# Kan geen cross detecteren  
              
        \# ... logica voor cross-detectie ...  
        \# (Aanname dat ema\_50 ook is aangevraagd en in state zit)  
        current\_ema\_slow \= context.computed\_values.indicators.get("indicator.ema.50")  
        prev\_ema\_slow \= self.state.get("last\_ema\_50")  
        self.state\["last\_ema\_50"\] \= current\_ema\_slow  
        self.commit\_state()  
          
        if prev\_ema\_fast \< prev\_ema\_slow and current\_ema\_fast \> current\_ema\_slow:  
             \# Genereer signaal...  
             pass  
               
        return \[\]

### **2.4. Impact op Manifesten en Validatie (Cruciale Wijziging)**

Het manifest.yaml wordt de **enige bron van waarheid** voor de data-behoeften van een plugin.

#### **2.4.1. De Herziene dependencies Sectie in manifest.yaml**

\# Voorbeeld manifest voor EMACrossOpportunity (GECORRIGEERD)  
dependencies:  
  \# Deze worker heeft GEEN directe 'environment\_data' nodig.  
  \# Zijn inputs zijn puur berekende waarden.  
  requires\_environment\_data: \[\]

  \# Welke 'berekende' data van andere ContextWorkers is nodig?  
  requires\_computed\_keys:  
    \- "indicator.ema.20"  
    \- "indicator.ema.50"  
capabilities:  
  \# Heeft state nodig om de vorige EMA-waarden zelf te onthouden.  
  state:  
    enabled: true

\# Voorbeeld manifest voor EMADetector  
dependencies:  
  requires\_environment\_data: \["ohlcv\_df"\]  
  produces\_dto: "backend.shared\_dtos.context\_update.ContextUpdateDTO"  
  produces\_keys: \["indicator.ema.20", "indicator.ema.50"\]

#### **2.4.2. De Aangescherpte Rol van de DependencyValidator**

De rol van de DependencyValidator wordt cruciaal. Voorafgaand aan elke run moet deze:

1. De volledige "stamboom" van data-vereisten (requires\_\*) en data-producties (produces\_\*) voor de *gehele* strategie in kaart brengen.  
2. Valideren dat elke requires\_computed\_keys wordt voldaan door een produces\_keys van een ContextWorker die *eerder* in de sequentiële pijplijn wordt uitgevoerd.  
3. Een "boodschappenlijst" van requires\_environment\_data opstellen, zodat de ExecutionEnvironment en ContextOperator precies weten welke ruwe data ze moeten laden en doorgeven, wat de performance optimaliseert.

### **2.5. Voordelen van de v2 Architectuur**

* **Maximale Explicietheid:** De data-behoefte van elke plugin is 100% gedeclareerd. "Verborgen" afhankelijkheden van data in de TradingContext zijn onmogelijk.  
* **Single Responsibility Principe Versterkt:** De worker is volledig verantwoordelijk voor zijn eigen staat en geschiedenis. Het platform faciliteert slechts de persistentie.  
* **Geoptimaliseerde Performance:** De ExecutionEnvironment hoeft alleen de data te laden en te verstrekken waar expliciet om gevraagd wordt door de gebruikte plugins.  
* **Verbeterde Testbaarheid:** Het testen van een worker wordt nog eenvoudiger. Je hoeft alleen een TradingContext te construeren met de data die in zijn requires\_\* velden is gespecificeerd.  
* **Live-First Architectuur:** Het model is nu conceptueel identiek voor backtesting en live trading, zonder het "gedrocht" van een enriched\_df.

## **3\. Conclusie**

De "Point-in-Time" architectuur is een fundamentele stap naar een robuuster, testbaarder en conceptueel zuiverder systeem. Het elimineert de impliciete afhankelijkheden en inefficiënties van de enriched\_df en dwingt een expliciet, DTO-gedreven contract af voor alle data-uitwisseling. Hoewel dit een aanzienlijke impact heeft op de oorspronkelijke ontwerpen, legt het de juiste, solide basis voor een financiële applicatie waar geen ruimte is voor compromissen op het gebied van veiligheid en reproduceerbaarheid.