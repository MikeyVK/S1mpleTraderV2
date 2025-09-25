# 1. Backtest Workflow

Dit document beschrijft de dataflow en de verantwoordelijkheden van de componenten tijdens een enkele backtest-run. De architectuur volgt een "lopende band" model, in lijn met het **Single Responsibility Principle** en het **Strategy Pattern** zoals beschreven in het `1_ARCHITECTURE.md` document.

## 1.1. Het Specialistenteam

De workflow wordt uitgevoerd door een reeks specialisten, elk met één duidelijke taak. Een trade-idee wordt stapsgewijs verrijkt terwijl het langs deze specialisten passeert.

1.  **`PatternDetector`** (De Verkenner): Scant marktdata naar ruwe, potentiële kansen.
2.  **`MatchFilter`** (De Poortwachter): Past objectieve filters toe op de ruwe kansen.
3.  **`ExecutionPlanner`** (De Timing Expert): Bepaalt de precieze entry-tactiek (prijs, ordertype).
4.  **`ExitPlanner`** (De Strateeg): Definieert de initiële risicoparameters (stop-loss en take-profit prijzen).
5.  **`SizePlanner`** (De Logistiek Manager): Berekent de uiteindelijke positiegrootte op basis van risico en kapitaal.
6.  **`TradeRefiner`** (De Specialist): Een optionele component die een compleet trade-plan kan aanpassen of vetoën op basis van geavanceerde regels.
7.  **`OrderRouter`** (De Uitvoerder): Vertaalt het plan naar een specifiek order (voornamelijk voor live trading).
8.  **`Portfolio`** (De Boekhouder): Een "domme" component die enkel de uiteindelijke orders uitvoert en de rekeningstaat bijhoudt.

---

## 1.2. De Dataflow: Van Idee tot Trade

Het proces is een eenrichtingsstroom van data. Elke specialist geeft een specifiek **Data Transfer Object (DTO)** door aan de volgende. Een overkoepelend **`TradingContext`** object (de "gereedschapskist") wordt aan alle relevante specialisten doorgegeven om hen van de nodige context te voorzien (bv. prijsdata, balans).

**Input:** `[price_data]` (DataFrame) & `TradingContext` (Gereedschapskist)

1.  **Actor:** `PatternDetector` & `MatchFilter`
    * **Output:** `PatternMatch` (DTO)
    * *Inhoud:* `timestamp`, `asset`, `direction`

2.  **Actor:** `ExecutionPlanner`
    * **Input:** `PatternMatch`
    * **Output:** `ExecutionSignal` (DTO)
    * *Inhoud:* Alle data van `PatternMatch` + `entry_price`, `entry_method`, `rules` (Set)

3.  **Actor:** `ExitPlanner`
    * **Input:** `ExecutionSignal`
    * **Output:** `PricedSignal` (DTO)
    * *Inhoud:* Alle data van `ExecutionSignal` + `sl_price`, `tp_price`. De `rules` set kan worden aangevuld.

4.  **Actor:** `SizePlanner`
    * **Input:** `PricedSignal`
    * **Output:** `Trade` (DTO)
    * *Inhoud:* Alle data van `PricedSignal` + `position_value_eur`, `position_size_asset`.

5.  **Actor:** `TradeRefiner`(s)
    * **Input:** `Trade`
    * **Output:** Een (mogelijk aangepast) `Trade` object.

6.  **Actor:** `OrderRouter`
    * **Input:** Het finale `Trade` object.
    * **Output:** `ExecutionOrder` (DTO)
    * *Inhoud:* `asset`, `direction`, `quantity`, `order_type`, `params`.

7.  **Actor:** `Portfolio`
    * **Input:** `ExecutionOrder`
    * **Actie:** Voert het order uit en werkt de interne staat bij.

---

## 1.3. DTO Woordenlijst

| DTO Naam | Gecreëerd Door | Rol / Inhoud |
| :--- | :--- | :--- |
| `PatternMatch` | `PatternDetector` / `MatchFilter` | De ruwe, gefilterde kans (wat, waar, wanneer). |
| `ExecutionSignal` | `ExecutionPlanner` | Een `PatternMatch` met een concrete entry-tactiek. |
| `PricedSignal` | `ExitPlanner` | Een `ExecutionSignal` met absolute SL/TP prijzen. |
| `Trade` | `SizePlanner` / `TradeRefiner` | Het finale, complete en uitvoerbare trade-plan. |
| `ExecutionOrder` | `OrderRouter` | De specifieke instructies voor het `Portfolio` of de exchange. |
| `TradingContext` | `BacktestService` | De "gereedschapskist" met alle contextuele data (`price_data`, `balance`, etc.). |