# 5. Frontend Integratie in V2

Deze architectuur is ontworpen met een rijke, dynamische frontend als einddoel. De scheiding tussen backend en frontend wordt mogelijk gemaakt door de zelfbeschrijvende aard van de plugins.

### 5.1. Dynamische UI-Generatie

Een web-based frontend (bv. gebouwd in React/Vue met TypeScript) hoeft geen hardgecodeerde kennis te hebben van de beschikbare strategie-componenten.

1.  **Plugin Discovery API:** De frontend roept een API-endpoint aan (`/api/plugins`) die de `plugin_manifest.yaml` bestanden van alle geïnstalleerde plugins retourneert.
2.  **Automatische UI-Opbouw:** Op basis van de ontvangen metadata bouwt de UI zichzelf op. Een plugin met `type: "signal_refiner"` verschijnt automatisch in het "Signal Refinement" paneel van de strategie-bouwer.
3.  **Automatische Configuratie-Formulieren:** De `schema.py` van een plugin wordt gebruikt om dynamisch een configuratieformulier te genereren met de juiste veld-types en validatieregels.

### 5.2. De Rol van TypeScript: Contractuele Zekerheid

TypeScript is de tegenhanger van Pydantic en essentieel voor een robuuste full-stack applicatie.

* **Code Generatie:** Pydantic-modellen uit de `schema.py` van elke plugin worden automatisch omgezet naar TypeScript `interfaces`.
* **Type-Veilige API-Communicatie:** De frontend weet *exact* welke datastructuur te verwachten van de backend API. Een wijziging in een Pydantic-model die niet wordt doorgevoerd in de frontend leidt tot een compile-time fout, niet tot een runtime bug.
* **Resultaat:** Dit creëert een volledig ontkoppeld maar contractueel gebonden ecosysteem, waardoor de frontend en backend onafhankelijk van elkaar kunnen evolueren zolang ze zich aan de contracten (de Pydantic-modellen en TypeScript-interfaces) houden.