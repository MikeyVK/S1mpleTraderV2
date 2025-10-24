# Security Architectuur: Permissions & Validatie

**Versie:** 3.0
**Status:** Definitief

Dit document beschrijft de security-architectuur van S1mpleTrader, inclusief plugin permissions, configuratie validatie en data beveiliging.

---

## **Inhoudsopgave**

1. [Executive Summary](#executive-summary)
2. [Plugin Security & Permissions](#plugin-security--permissions)
3. [Configuratie Validatie](#configuratie-validatie)
4. [Data Beveiliging](#data-beveiliging)
5. [Best Practices](#best-practices)

---

## **Executive Summary**

De security-architectuur van S1mpleTrader is ontworpen om het systeem te beschermen tegen malafide of buggy plugins, ongeldige configuraties en datalekken.

### **Kernkenmerken**

**1. Plugin Permissions**
- Expliciete permissies in `manifest.yaml` voor netwerk- en bestandssysteemtoegang
- PluginRegistry valideert permissies tijdens bootstrap
- ExecutionEnvironment dwingt permissies af tijdens runtime

**2. Configuratie Validatie**
- Strikte Pydantic schemas voor alle YAML configuratiebestanden
- Cross-file referentie validatie
- Event chain validatie om ongeldige event flows te voorkomen

**3. Data Beveiliging**
- Environment variable substitution voor secrets
- Gescheiden data-, state- en journal-opslag
- Toegangscontrole via PersistorFactory

**4. Fail-Fast Principe**
- Systeem start niet op bij ongeldige configuratie
- Duidelijke, traceerbare foutmeldingen

---

## **Plugin Security & Permissions**

### **Manifest-Gedreven Permissions**

Plugins moeten expliciet permissies aanvragen in hun `manifest.yaml`.

```yaml
# plugins/my_plugin/manifest.yaml
permissions:
  network_access:
    - "https://api.kraken.com"
    - "https://api.binance.com"
  filesystem_access:
    - "/data/my_plugin_data/"
```

### **Validatie en Handhaving**

1. **PluginRegistry:** Valideert de `permissions` sectie tijdens het scannen van plugins.
2. **ExecutionEnvironment:** Dwingt de permissies af tijdens runtime. Een plugin die probeert toegang te krijgen tot een niet-gedeclareerde resource zal een `PermissionError` veroorzaken.

---

## **Configuratie Validatie**

### **Pydantic Schemas**

Alle configuratiebestanden worden gevalideerd door Pydantic schemas. Dit garandeert type-veiligheid en structurele correctheid.

### **Cross-File Referentie Validatie**

De `ConfigValidator` controleert of alle ID-referenties tussen bestanden geldig zijn:
- `connector_id` in `environments.yaml` moet bestaan in `connectors.yaml`
- `strategy_blueprint_id` in `operation.yaml` moet verwijzen naar een bestaand blueprint-bestand
- `plugin` namen in `strategy_blueprint.yaml` moeten overeenkomen met geregistreerde plugins

### **Event Chain Validatie**

De `EventChainValidator` voorkomt runtime problemen door de event flow statisch te analyseren:
- Detecteert orphaned events (geen subscribers)
- Detecteert dead-end events (geen publishers)
- Voorkomt circular dependencies

---

## **Data Beveiliging**

### **Secrets Management**

Secrets (API keys, etc.) worden beheerd via environment variables en gesubstitueerd in de configuratie.

```yaml
# config/connectors.yaml
kraken_live_eur_account:
  type: "kraken_private"
  api_key: "${KRAKEN_API_KEY}"
  api_secret: "${KRAKEN_API_SECRET}"
```

### **Data Isolatie**

De `PersistorFactory` zorgt voor data-isolatie door persistors te creëren met specifieke, beperkte paden:
- `state/{worker_id}/state.json`
- `journals/{strategy_id}/journal.json`

---

## **Best Practices**

- **Minimale Permissies:** Vraag alleen de permissies aan die absoluut noodzakelijk zijn.
- **Valideer Input:** Valideer alle externe data en configuratie.
- **Gebruik Secrets Management:** Hardcode nooit secrets in configuratiebestanden.
- **Regelmatige Audits:** Controleer periodiek de permissies van alle plugins.

---

## **Referenties**

- **[Plugin Anatomy](03_Development/01_Plugin_Anatomy.md)** - Manifest configuratie
- **[Configuration Hierarchy](02_Core_Concepts/03_Configuration_Hierarchy.md)** - Validatie schemas
- **[Event Architecture](02_Core_Concepts/02_Event_Architecture.md)** - Event chain validatie

---

**Einde Document**