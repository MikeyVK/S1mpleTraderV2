# Revisieplan voor S1mpleTrader V2 Architectuur

Dit document beschrijft de gedetailleerde, hoofdstuk-per-hoofdstuk inventarisatie van de wijzigingen die nodig zijn voor het hoofddocument `S1mpleTrader V2 Architectuur.md`. De wijzigingen zijn gebaseerd op de fundamentele architecturale verschuivingen zoals beschreven in de addenda, met name de eliminatie van de Operator-laag en de introductie van een "Point-in-Time", DTO-gedreven data-architectuur.

---

## **Hoofdstuk 1: De Communicatie Architectuur**

**Status:** Fundamenteel achterhaald. Vereist een volledige herschrijving.

**Te Verwijderen Concepten:**
- Het EventAdapter Patroon dat zich richt op het koppelen van *Operators* aan de EventBus.
- De `Operator Suite` (paragraaf 1.8).
- De beschrijving van de bootstrap-fase waarbij de `EventWiringFactory` een globale `wiring_map.yaml` leest om Operators te bedraden.

**Nieuwe Inhoud:**
1.  **Kernfilosofie:** Introduceer het "platgeslagen" netwerkmodel waarin *elke* communicerende component (worker of singleton) een eigen, generieke `EventAdapter` krijgt.
2.  **De Generieke `EventAdapter`:** Beschrijf de rol van de adapter als een "domme" uitvoerder van communicatie-instructies, geconfigureerd door `BuildSpecs`.
3.  **De `DispositionEnvelope`:** Leg uit hoe workers hun intentie (CONTINUE, PUBLISH, STOP) communiceren aan hun adapter zonder directe kennis van de EventBus.
4.  **Gescheiden Communicatiepaden:** Maak een helder onderscheid tussen:
    *   **Interne Data Flow (via `TickCache`):** Voor het doorgeven van intermediaire resultaten (plugin-specifieke DTO's) tussen workers binnen één tick.
    *   **Externe Communicatie (via `EventBus`):** Voor het publiceren van significante, asynchrone signalen en alerts (standaard Systeem DTO's).
5.  **De Gesplitste `wiring_map`:** Leg de nieuwe configuratie uit:
    *   `platform_wiring_map.yaml`: Voor statische, operation-brede singletons.
    *   `base_wiring.yaml`: Als template voor de UI.
    *   `strategy_wiring_map.yaml`: Het door de UI gegenereerde, expliciete bedradingsschema voor een specifieke strategie.
6.  **De Nieuwe Bootstrap Flow:** Beschrijf de rol van de `ConfigTranslator` die alle wiring-maps combineert in een `wiring_spec` binnen de `BuildSpecs`, en de `EventWiringFactory` die deze spec gebruikt om de adapters te configureren.

---

## **Hoofdstuk 2: Architectuur & Componenten**

**Status:** Gedeeltelijk achterhaald. Kernstructuur blijft, maar de orkestratie- en datalaag moeten volledig worden herschreven.

**Te Verwijderen Concepten:**
- Het concept van de `BaseOperator` en de data-gedreven operator (paragraaf 2.7).
- De beschrijving van de `ContextBuilder` als startpunt van de bootstrap.

**Nieuwe Inhoud:**
1.  **Worker Ecosysteem (2.4):** De 5 worker-categorieën blijven bestaan, maar de beschrijving van hun aansturing moet worden aangepast. Ze worden niet langer beheerd door Operators, maar worden direct aan elkaar gekoppeld via de `strategy_wiring_map`.
2.  **Dataflow & Orkestratie (2.11):** Dit moet volledig worden herschreven.
    *   Verwijder de Operator-gedreven dataflow.
    *   Introduceer de **Point-in-Time Architectuur**:
        *   De `TradingContext` is minimalistisch (timestamp, prijs).
        *   De `ITradingContextProvider` is de centrale hub voor data-toegang.
        *   De `TickCache` is de tijdelijke opslag voor intermediaire DTO's binnen één tick.
3.  **Assembly Components (2.10):** De rollen van de factories moeten worden bijgewerkt om hun afhankelijkheid van `BuildSpecs` te reflecteren. De `OperationService` is nu de initiator van de `ContextBuilder` (of de vervanger daarvan).
4.  **Dependency Validator:** Voeg de `DependencyValidator` toe als een cruciale component in de assembly-laag die de logische consistentie van de `strategy_wiring_map` valideert.

---

## **Hoofdstuk 3: De Configuratie Trein**

**Status:** Gedeeltelijk achterhaald. De hiërarchie en het vertaalproces zijn significant veranderd.

**Te Verwijderen Concepten:**
- `operators.yaml`.

**Nieuwe Inhoud:**
1.  **De Drie Configuratielagen (Nieuw Concept):** Introduceer de strikte hiërarchie zoals beschreven in Addendum 3.8:
    *   **Laag 1: `PlatformConfig`** (globale, statische instellingen).
    *   **Laag 2: `OperationConfig`** (de "werkruimte" met connectors, environments, etc.).
    *   **Laag 3: `StrategyConfig`** (de blauwdruk voor één strategie).
2.  **De Rol van `wiring_map.yaml`:** Herschrijf de beschrijving om de splitsing in `platform_wiring_map`, `base_wiring` en de UI-gegenereerde `strategy_wiring_map` te reflecteren.
3.  **De `ConfigTranslator` en `BuildSpecs`:** Dit is een nieuw, centraal concept. Beschrijf hoe de `ConfigTranslator` de drie configuratielagen leest en vertaalt naar machine-leesbare `BuildSpecs`.
4.  **De "Configuratie Trein in Actie" (3.8):** Herschrijf deze paragraaf volledig om de nieuwe flow te tonen: `OperationService` -> `ConfigLoader` -> `ConfigValidator` -> `ConfigTranslator` -> `BuildSpecs` -> Factories.

---

## **Hoofdstuk 4: De Anatomie van een Plugin**

**Status:** Gedeeltelijk achterhaald. De interactie van een worker met de buitenwereld is fundamenteel veranderd.

**Nieuwe Inhoud:**
1.  **Dependencies (4.3.2):** Vervang de beschrijving van `requires` en `provides` (DataFrame kolommen) volledig.
    *   Introduceer `requires_capability`: voor het aanvragen van platform-providers (bv. `ohlcv_window`, `state_persistence`).
    *   Introduceer `requires_dtos`: voor het declareren van afhankelijkheden van DTO's geproduceerd door andere workers.
    *   Introduceer `produces_dtos`: voor het declareren van de eigen DTO-output voor de `TickCache`.
2.  **Worker Implementatie (4.4):** Herschrijf de codevoorbeelden en de beschrijving van de `process`-methode.
    *   Toon hoe een worker de `ITradingContextProvider` en andere providers (geïnjecteerd in `__init__`) gebruikt om data op te vragen.
    *   Toon hoe een worker `set_result_dto()` gebruikt om intermediaire resultaten in de `TickCache` te plaatsen.
    *   Toon hoe een worker een `DispositionEnvelope` retourneert om zijn intentie (CONTINUE, PUBLISH, STOP) aan te geven.

---

## **Hoofdstuk 5: De Workflow Orkestratie**

**Status:** Volledig achterhaald. Dit hoofdstuk moet van de grond af aan opnieuw worden geschreven.

**Nieuwe Inhoud:**
- Dit hoofdstuk moet de "platgeslagen", expliciet bedrade orkestratie beschrijven.
- **De Rol van de `strategy_wiring_map`:** Leg uit hoe dit UI-gegenereerde bestand de *enige* bron van waarheid is voor de flow binnen een strategie.
- **De Rol van de `EventAdapter`:** Beschrijf hoe de adapters de `wiring_map` uitvoeren door workers aan te roepen en hun `DispositionEnvelope` te interpreteren.
- **Data Flow via `TickCache`:** Visualiseer en beschrijf de "Point-in-Time" dataflow: een event triggert de `TickCacheManager`, die de `ITradingContextProvider` configureert. Workers worden aangeroepen, vragen DTO's op bij de provider, en plaatsen nieuwe DTO's terug in de cache voor de volgende stap in de keten.
- **Systeem vs. Custom Events:** Leg het onderscheid uit dat nu door de `DispositionEnvelope` wordt beheerd.

---

## **Hoofdstuk 6: Frontend Integratie**

**Status:** Gedeeltelijk achterhaald. De rol van de UI is belangrijker en anders.

**Te Verwijderen Concepten:**
- De "Operator Configuration UI".

**Nieuwe Inhoud:**
- **De Strategy Builder als "Wiring Editor":** De UI is niet langer een simpele configurator, maar een visuele editor die de `strategy_wiring_map.yaml` genereert. Beschrijf hoe de UI de gebruiker in staat stelt om workers serieel of parallel te "bedraden" en hoe het de manifesten van plugins leest om event-gebaseerde verbindingen te suggereren en valideren.

---

## **Hoofdstuk 8: Ontwikkelstrategie & Tooling**

**Status:** Gedeeltelijk achterhaald. De workflow voor ontwikkelaars is veranderd.

**Nieuwe Inhoud:**
- **Development Workflow (8.6):** Update de codevoorbeelden om de nieuwe interactiepatronen te tonen:
    - Dependency injection van providers in `__init__`.
    - Gebruik van `ITradingContextProvider`.
    - Retourneren van `DispositionEnvelope`.
- **Testing (8.7):** Werk de teststrategieën bij. Toon hoe de `ITradingContextProvider` en andere platform-providers gemockt moeten worden in unit tests om de worker-logica geïsoleerd te testen.

---

## **Overige Hoofdstukken**

- **Hoofdstuk 7 (Resilience):** De principes blijven gelijk, maar de implementatievoorbeelden moeten worden bijgewerkt om de nieuwe provider-interfaces (`IStateProvider`, `IJournalWriter`) te gebruiken.
- **Hoofdstuk 9 (Meta Workflows):** Het concept blijft hetzelfde, maar de beschrijving van hoe de `OperationService` een enkele run opzet, moet worden bijgewerkt om de nieuwe bootstrap-flow (via `ConfigTranslator` en `BuildSpecs`) te reflecteren.
- **Hoofdstuk 10 (Coding Standaarden):** De principes blijven geldig, maar alle codevoorbeelden die naar de `BaseOperator` of de oude dataflow verwijzen, moeten worden vervangen door voorbeelden uit de nieuwe architectuur.
