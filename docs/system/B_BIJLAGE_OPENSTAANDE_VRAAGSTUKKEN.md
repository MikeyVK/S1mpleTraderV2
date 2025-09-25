Bijlage B: Openstaande Vraagstukken & Onderzoekspunten
Dit document bevat een lijst van bekende "onbekenden" en complexe vraagstukken die tijdens de detailimplementatie van de V2-architectuur verder onderzocht en opgelost moeten worden. Ze worden hier vastgelegd om te verzekeren dat ze niet vergeten worden.

B.1. State Management voor Stateful Plugins

Vraagstuk: Hoe persisteren, beheren en herstellen we de staat van stateful plugins (bv. een Grid Trading-strategie die zijn openstaande grid-levels moet onthouden) op een robuuste manier, met name na een applicatiecrash?

Zie ook: docs/system/6_RESILIENCE_AND_OPERATIONS.md

B.2. Data Synchronisatie in Live Omgevingen

Vraagstuk: Hoe gaat de LiveEnvironment om met asynchrone prijs-ticks die voor verschillende assets op verschillende momenten binnenkomen? Moet de orkestratie tick-gedreven zijn (complexer, maar nauwkeuriger) of bar-gedreven (eenvoudiger, maar met mogelijke vertraging)?

B.3. Performance en Geheugengebruik

Vraagstuk: Wat is de meest efficiënte strategie voor het beheren van geheugen bij grootschalige Multi-Time-Frame (MTF) analyses, met name wanneer dit over meerdere assets parallel gebeurt? Hoe voorkomen we onnodige duplicatie van data in het geheugen?

B.4. Debugging en Traceability

Vraagstuk: Welke tools of modi moeten we ontwikkelen om het debuggen van complexe, parallelle runs te faciliteren? Hoe kan een ontwikkelaar eenvoudig de volledige levenscyclus van één specifieke trade volgen (traceability) door alle lagen en plugins heen?

Zie ook: Het concept van een Correlation ID in docs/development/KanBan/product_backlog.csv.