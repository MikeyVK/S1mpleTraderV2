# **8\. Meta Workflows: Van Analyse tot Inzicht**

Versie: 2.0 (Architectuur Blauwdruk v4)  
Status: Definitief  
Dit document beschrijft de architectuur en de rol van de "Meta Workflows". Dit zijn hoog-niveau services die bovenop de kern-executielogica draaien om geavanceerde analyses, optimalisaties en automatisering mogelijk te maken.

## **8.1. Concept: De Operations-service als Motor**

De Operations-service, aangestuurd via het run\_operation.py entrypoint, is de motor die in staat is om **één enkele, volledig gedefinieerde Operation** uit te voeren. Meta Workflows zijn services in de Service-laag die deze motor herhaaldelijk en systematisch aanroepen, met steeds een andere configuratie, om complexe, kwantitatieve vragen te beantwoorden.

Ze fungeren als "onderzoekleiders" die de Operations-service als een "black box"-motor gebruiken. Ze leunen zwaar op een ParallelRunService om duizenden backtests efficiënt en parallel uit te voeren. Waar optimalisatie in V1 een ad-hoc script was, wordt het in V2 een **"eerste klas burger"** van de architectuur.

## **8.2. De OptimizationService (Het Onderzoekslab)**

* **Doel:** Het systematisch doorzoeken van een grote parameterruimte om de meest performante combinaties voor een strategie te vinden.  
* **Analogie:** Een farmaceutisch lab dat duizenden moleculaire variaties test om het meest effectieve medicijn te vinden.

#### **Gedetailleerde Workflow:**

1. **Input (Het Onderzoeksplan):** De service vereist een **basis operation.yaml** die de te testen strategy\_link bevat, en een **optimization.yaml** die de onderzoeksvraag definieert: welke parameters (start, end, step) in de gelinkte strategy\_blueprint.yaml moeten worden gevarieerd.  
2. **Proces (De Experimenten):**  
   * De OptimizationService genereert een volledige lijst van alle mogelijke parameter-combinaties.  
   * Voor elke combinatie creëert het:  
     1. Een unieke, **tijdelijke strategy\_blueprint.yaml** waarin de parameters zijn aangepast.  
     2. Een unieke, **tijdelijke en uitgeklede operation.yaml** die slechts één strategy\_link bevat: die naar de zojuist gecreëerde tijdelijke blueprint en de relevante backtest-omgeving.  
   * Het delegeert de volledige lijst van paden naar deze tijdelijke operation.yaml\-bestanden aan de ParallelRunService.  
3. **Executie (Het Robotleger):**  
   * De ParallelRunService start een pool van workers (één per CPU-kern).  
   * Elke worker ontvangt een pad naar een unieke operation.yaml, roept de Operations-service aan via run\_operation.py en voert een volledige backtest uit.  
4. **Output (De Analyse):**  
   * De OptimizationService verzamelt alle BacktestResult-objecten.  
   * Het creëert een pandas DataFrame met de geteste parameters en de resulterende performance-metrieken.  
   * Deze data wordt naar de Web UI gestuurd voor presentatie in een interactieve, sorteerbare tabel.

## **8.3. De VariantTestService (De Vergelijkings-Arena)**

* **Doel:** Het direct vergelijken van een klein aantal discrete strategie-varianten onder exact dezelfde marktomstandigheden om de robuustheid en de impact van specifieke keuzes te valideren.  
* **Analogie:** Een "head-to-head" race tussen een paar topatleten om te zien wie de beste allrounder is.

#### **Gedetailleerde Workflow:**

1. **Input (De Deelnemers):** De service vereist een **basis operation.yaml** en een **variant.yaml** die de "deelnemers" definieert door middel van "overrides" op de gelinkte strategy\_blueprint.yaml.  
   * **Voorbeeld:**  
     * **Variant A ("Baseline"):** De basisconfiguratie.  
     * **Variant B ("Hoge RR"):** Overschrijft alleen de risk\_reward\_ratio parameter in een specifieke plugin.  
     * **Variant C ("Andere Exit"):** Vervangt de ATR exit-plugin door een FixedPercentage exit-plugin.  
2. **Proces (De Race-Opzet):**  
   * De VariantTestService past voor elke gedefinieerde variant de "overrides" toe op de basis-blueprint om unieke, **tijdelijke strategy\_blueprint.yaml**\-bestanden te creëren.  
   * Vervolgens creëert het voor elke variant een **tijdelijke, uitgeklede operation.yaml** die naar de juiste tijdelijke blueprint linkt.  
   * Het delegeert de lijst van paden naar deze operation.yaml\-bestanden aan de ParallelRunService.  
3. **Executie (Het Startschot):**  
   * De ParallelRunService voert voor elke variant een volledige backtest uit door de Operations-service aan te roepen met het juiste operation.yaml\-bestand.  
4. **Output (De Finishfoto):**  
   * De VariantTestService verzamelt de BacktestResult-objecten.  
   * Deze data wordt naar de Web UI gestuurd voor een directe, visuele vergelijking, bijvoorbeeld door de equity curves van alle varianten in één grafiek te plotten.

## **8.4. De Rol van ParallelRunService**

Deze service is een cruciale, herbruikbare Backend-component. Zowel de OptimizationService als de VariantTestService zijn "klanten" van deze service. Zijn enige verantwoordelijkheid is het efficiënt managen van de multiprocessing-pool, het tonen van de voortgang en het netjes aggregeren van resultaten. Dit is een perfect voorbeeld van het **Single Responsibility Principle**.