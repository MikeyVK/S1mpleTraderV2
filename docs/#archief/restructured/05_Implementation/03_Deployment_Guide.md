# Deployment Gids: Installatie & Configuratie

**Versie:** 3.0
**Status:** Definitief

Dit document beschrijft de stappen voor het installeren, configureren en deployen van het S1mpleTrader-systeem.

---

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Systeemvereisten](#systeemvereisten)
3. [Installatie](#installatie)
4. [Configuratie](#configuratie)
5. [Deployment](#deployment)
6. [Best Practices](#best-practices)

---

## **Executive Summary**

Deze gids biedt een stapsgewijze handleiding voor het opzetten van het S1mpleTrader-systeem, van installatie tot deployment.

### **Kernstappen**

1. **Installatie:** Installeer Python, dependencies en eventuele externe tools.
2. **Configuratie:** Configureer de `platform.yaml`, `connectors.yaml`, `environments.yaml` en andere kernbestanden.
3. **Deployment:** Start de applicatie via de juiste entrypoint (`run_web.py`, `run_backtest_cli.py`, `run_supervisor.py`).

---

## **Systeemvereisten**

- **Python:** 3.9+
- **Dependencies:** Zie `requirements.txt`
- **OS:** Linux, macOS, Windows
- **Hardware:** Minimaal 4GB RAM, 2 CPU cores

---

## **Installatie**

1. **Clone de repository:**
   ```bash
   git clone https://github.com/s1mpletrader/s1mpletrader.git
   cd s1mpletrader
   ```

2. **Installeer dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## **Configuratie**

### **1. `platform.yaml`**

Configureer globale instellingen zoals logging, taal en bestandspaden.

```yaml
# config/platform.yaml
language: "nl"
logging:
  profile: "analysis"
plugins_root_path: "plugins"
data_root_path: "data"
```

### **2. `connectors.yaml`**

Configureer API-verbindingen met exchanges. Gebruik environment variables voor secrets.

```yaml
# config/connectors.yaml
kraken_live_eur_account:
  type: "kraken_private"
  api_key: "${KRAKEN_API_KEY}"
  api_secret: "${KRAKEN_API_SECRET}"
```

### **3. `environments.yaml`**

Definieer de execution environments (backtest, paper, live).

```yaml
# config/environments.yaml
live_kraken_main:
  type: "live"
  connector_id: "kraken_live_eur_account"

backtest_2020_2024_btc:
  type: "backtest"
  data_source_id: "btc_eur_15m_archive"
```

---

## **Deployment**

### **Web UI (Development)**

Start de web UI voor strategie-ontwikkeling en analyse.

```bash
python run_web.py
```

### **Backtest (CLI)**

Voer een backtest uit via de command-line.

```bash
python run_backtest_cli.py --operation my_btc_operation
```

### **Live Trading (Supervisor)**

Start de live trading-omgeving met de supervisor voor crash recovery.

```bash
python run_supervisor.py --operation my_live_operation
```

---

## **Best Practices**

- **Gebruik Environment Variables:** Hardcode nooit secrets.
- **Valideer Configuratie:** Gebruik de `ConfigValidator` tool voor deployment.
- **Monitor Logs:** Houd de logs in de gaten voor errors en warnings.
- **Backup State:** Maak regelmatig backups van de `state/` en `journals/` directories.

---

## **Referenties**

- **[Configuration Hierarchy](02_Core_Concepts/03_Configuration_Hierarchy.md)** - Details over alle configuratiebestanden
- **[Security Architectuur](04_System_Architecture/04_Security_Architecture.md)** - Secrets management

---

**Einde Document**