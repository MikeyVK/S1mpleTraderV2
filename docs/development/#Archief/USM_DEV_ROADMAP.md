Release 1: The Walking Skeleton (MVP)
Doel: Een strategie kunnen bouwen, een enkele backtest uitvoeren en de basisresultaten (PnL & trades) kunnen zien.

PLUGIN DEVELOPMENT	STRATEGY BUILDER	BACKTESTING & ANALYSIS	PAPER TRADING	LIVE MONITORING
[DEV] Plugin-idee beschrijven.	[UI] Nieuwe strategie aanmaken in de web-UI.	[UI] Een enkele backtest-run starten.		
[DEV] Nieuwe plugin ontwikkelen (worker, schema, manifest).	[UI] Beschikbare plugins per fase tonen.	[UI] Basis-resultatenpagina met PnL-grafiek en key metrics.		
[DEV] Plugin testen (unit test).	[UI] Plugins toevoegen aan de 6 fasen.	[UI] Lijst van alle trades tonen in een simpele tabel.		
[UI] Plugin-parameters instellen via een formulier.			
[UI] Strategie opslaan.			

Exporteren naar Spreadsheets
Release 2: Advanced Analysis & Tooling
Doel: De strateeg krachtige tools geven om strategieën te optimaliseren, te vergelijken en diepgaand visueel te analyseren.

PLUGIN DEVELOPMENT	STRATEGY BUILDER	BACKTESTING & ANALYSIS	PAPER TRADING	LIVE MONITORING
[UI] Een optimalisatie-run opzetten.		
[UI] Te optimaliseren parameters en ranges definiëren.		
[UI] Interactieve tabel voor optimization-resultaten (sorteren, filteren).		
[UI] Een varianten-test opzetten om kandidaten te vergelijken.		
[UI] Vergelijkende resultaten tonen (equity curves, heatmap).		
[UI] "Trade Explorer": diepgaande visuele analyse van enkele trades met context.		

Exporteren naar Spreadsheets
Release 3: Live Operations
Doel: De gevalideerde strategie veilig en betrouwbaar in een gesimuleerde (paper) en uiteindelijk live omgeving draaien.

PLUGIN DEVELOPMENT	STRATEGY BUILDER	BACKTESTING & ANALYSIS	PAPER TRADING	LIVE MONITORING
[UI] Strategie selecteren voor paper trading.	[UI] Dashboard voor live-portfolio monitoring.
[UI] Paper trading sessie starten/stoppen.	[UI] Live PnL, open posities en alerts tonen.
[UI] Real-time PnL en open posities bekijken.	[UI] Noodstop-knop.
[BE] PaperTradeEnvironment implementeren.	[BE] LiveEnvironment & run_supervisor.py implementeren.
[BE] Resilience-strategieën implementeren.