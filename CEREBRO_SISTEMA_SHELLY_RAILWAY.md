# 🧠 CÉREBRO DE SISTEMAS - Shelly Pro 3EM + Railway

**Sistema de Monitorização de Energia - Arquitetura PostgreSQL Only**

---

## 📊 VISÃO GERAL DO SISTEMA

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITETURA ATUAL                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Shelly Pro 3EM (192.168.0.245)                            │
│         ↓ HTTP Request a cada 60s                           │
│  collector-railway (Railway Worker)                         │
│         ↓ INSERT PostgreSQL                                 │
│  PostgreSQL Railway (tramway.proxy.rlwy.net:46128)         │
│         ↓                                                    │
│         ├─→ Grafana Railway (Dashboards)                    │
│         └─→ shelly-api-railway (Flask API)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Custo Mensal Estimado**: €0-5/mês
**Dependências**: Nenhuma (iMac eliminado)
**Base de Dados**: PostgreSQL Only (InfluxDB eliminado)

---

## 🔑 CREDENCIAIS E ACESSOS

### Railway - Projeto Principal
- **URL**: https://railway.app/
- **Project Token**: `cf2b7205-adf7-495b-a671-d32fdf0b8557`
- **Login**: Via GitHub (MarcioMiguel22)

### Grafana Railway
- **URL**: https://grafana-production-db87.up.railway.app/
- **Login**: Acesso Anónimo (Admin)
- **Configuração**:
  - `GF_AUTH_ANONYMOUS_ENABLED=true`
  - `GF_AUTH_ANONYMOUS_ORG_ROLE=Admin`

### PostgreSQL Railway (NOVO - tramway)
- **Host**: `tramway.proxy.rlwy.net`
- **Port**: `46128`
- **Database**: `railway`
- **User**: `postgres`
- **Password**: `RFVUeMxciMxzOFmwucLcDYqovaPEBEDb`
- **Connection String**:
  ```
  postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require
  ```

### PostgreSQL Railway (ANTIGO - switchback) - NÃO USAR
- **Host**: `switchback.proxy.rlwy.net`
- **Port**: `47559`
- **Database**: `railway`
- **User**: `postgres`
- **Password**: `qiUTzNhdGXGkDtpTDOoGRBJoAvwBLUub`
- **Status**: ⚠️ Base "Cérebro de Sistemas" - Manter para outros projetos

### InfluxDB Cloud (LEGADO - A ELIMINAR)
- **URL**: https://us-east-1-1.aws.cloud2.influxdata.com
- **Org**: MÁRCIOV ÁRIOSPRO
- **Token**: `rE69yYhRgXAzF0X7D37zkScPe_-ft1eWNUrmHTFFOoJc_lexGom5fFHsk-07eWxAztvBeOpcpN8Dpt7JyIdouw==`
- **Bucket**: energy
- **Status**: ⚠️ Dados migrados, pode ser desativado

### Shelly Pro 3EM
- **IP Local**: `192.168.0.245`
- **Endpoint**: `http://192.168.0.245/rpc/EM.GetStatus?id=0`
- **Autenticação**: Nenhuma (LAN)

---

## 🗄️ ESTRUTURA DA BASE DE DADOS

### Tabela: `shelly_power_readings`
**Descrição**: Leituras de potência (total + por fase)

```sql
CREATE TABLE shelly_power_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    phase VARCHAR(10) NOT NULL,        -- 'total', 'A', 'B', 'C'
    power_w REAL,                       -- Potência ativa (W)
    current_a REAL,                     -- Corrente (A)
    voltage_v REAL,                     -- Tensão (V)
    power_factor REAL,                  -- Fator de potência
    frequency_hz REAL,                  -- Frequência (Hz)
    UNIQUE (timestamp, device_id, phase)
);

CREATE INDEX idx_timestamp ON shelly_power_readings(timestamp);
CREATE INDEX idx_device_phase ON shelly_power_readings(device_id, phase);
```

**Queries Úteis**:
```sql
-- Total de registos
SELECT COUNT(*) FROM shelly_power_readings;

-- Potência média nas últimas 24h
SELECT AVG(power_w) as avg_power_w
FROM shelly_power_readings
WHERE phase = 'total'
  AND timestamp > NOW() - INTERVAL '24 hours';

-- Última leitura
SELECT * FROM shelly_power_readings
ORDER BY timestamp DESC LIMIT 1;

-- Potência total por hora (últimas 24h)
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(power_w) as avg_power_w,
    MAX(power_w) as max_power_w
FROM shelly_power_readings
WHERE phase = 'total'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
```

### Tabela: `shelly_phase_data`
**Descrição**: Dados detalhados por fase (potência reativa, aparente, etc.)

```sql
CREATE TABLE shelly_phase_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    phase VARCHAR(10) NOT NULL,
    active_power_w REAL,
    reactive_power_var REAL,
    apparent_power_va REAL,
    power_factor REAL,
    current_a REAL,
    voltage_v REAL
);
```

### Tabela: `shelly_energy_summary`
**Descrição**: Resumos de energia acumulada

```sql
CREATE TABLE shelly_energy_summary (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    total_energy_wh REAL,
    total_returned_wh REAL,
    by_minute_0_wh REAL,
    by_minute_1_wh REAL,
    by_minute_2_wh REAL
);
```

### Tabela: `shelly_device_info`
**Descrição**: Informações do dispositivo

```sql
CREATE TABLE shelly_device_info (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    last_seen TIMESTAMP,
    firmware_version VARCHAR(50),
    model VARCHAR(50)
);
```

---

## 🚀 COMO FAZER ALTERAÇÕES

### 1. Atualizar Collector (Railway Worker)

**Localização**: `/root/shelly-collector-railway/collect_shelly_postgres.py`

**Fazer Deploy**:
```bash
cd /root/shelly-collector-railway

# 1. Inicializar repositório Git (se ainda não existe)
git init
git add .
git commit -m "Update: Shelly collector changes"

# 2. Push para GitHub
git branch -M main
git remote add origin https://github.com/MarcioMiguel22/shelly-collector-railway.git
git push -u origin main

# 3. Railway faz deploy automático
```

**Variáveis de Ambiente no Railway**:
```bash
SHELLY_IP=192.168.0.245
DATABASE_URL=postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require
COLLECTION_INTERVAL=60
```

**Ver Logs**:
```bash
# Via Railway CLI
railway logs --service collector-railway

# Ou via API
curl -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer cf2b7205-adf7-495b-a671-d32fdf0b8557" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { deploymentLogs(...) }"}'
```

### 2. Atualizar Grafana Dashboards

**Método 1: Via Interface Web**
1. Acede a https://grafana-production-db87.up.railway.app/
2. Vai a **Dashboards** → **PostgreSQL - Dados Backup**
3. Clica em **Settings** (⚙️) → **JSON Model**
4. Edita o JSON e **Save Dashboard**

**Método 2: Via API (Programático)**
```python
import requests
import json

# 1. Exportar dashboard atual
response = requests.get(
    "https://grafana-production-db87.up.railway.app/api/dashboards/uid/postgres-backup-dashboard"
)
dashboard = response.json()['dashboard']

# 2. Fazer alterações
dashboard['title'] = "Novo Título"
# ... editar panels, queries, etc.

# 3. Reimportar
payload = {
    "dashboard": dashboard,
    "overwrite": True,
    "message": "Alterações via API"
}

response = requests.post(
    "https://grafana-production-db87.up.railway.app/api/dashboards/db",
    json=payload
)
print(response.json())
```

**Dashboard Atual**:
- **UID**: `shelly-3em-completo`
- **Título**: ⚡ Shelly Pro 3EM - Monitor Completo
- **URL**: https://grafana-production-db87.up.railway.app/d/shelly-3em-completo/
- **Auto-refresh**: 30 segundos
- **Time range**: Last 24 hours (ajustável)

**Secções do Dashboard**:
1. **📊 Visão Geral** - 4 stats principais (Potência, Corrente, Tensão, Frequência TOTAL)
2. **📈 Gráficos de Potência** - Potência total ao longo do tempo
3. **🔌 Potência por Fase** - Gráfico com fases A/B/C (cores: vermelho/amarelo/azul)
4. **⚡ Corrente e Tensão por Fase** - 2 gráficos lado a lado
5. **📊 Fator de Potência & Frequência** - Qualidade da energia
6. **📋 Dados Detalhados** - Tabela com últimas 50 leituras completas

**Dados Monitorizados**:
- Potência (W) - Total e por fase
- Corrente (A) - Total e por fase
- Tensão (V) - Média e por fase
- Fator de Potência - Por fase
- Frequência (Hz) - Da rede elétrica

### 3. Atualizar Datasource do Grafana

**Via API**:
```python
import requests

# Criar/Atualizar datasource
payload = {
    "name": "PostgreSQL - Shelly",
    "type": "postgres",
    "url": "tramway.proxy.rlwy.net:46128",
    "access": "proxy",
    "database": "railway",
    "user": "postgres",
    "secureJsonData": {
        "password": "RFVUeMxciMxzOFmwucLcDYqovaPEBEDb"
    },
    "jsonData": {
        "sslmode": "require",
        "postgresVersion": 1500
    },
    "uid": "postgres-shelly-backup-2025"
}

response = requests.post(
    "https://grafana-production-db87.up.railway.app/api/datasources",
    json=payload
)
print(response.json())
```

**Testar Datasource**:
```python
response = requests.get(
    "https://grafana-production-db87.up.railway.app/api/datasources/uid/postgres-shelly-backup-2025"
)
print(response.json())
```

### 4. Modificar Base de Dados

**Conectar via psql**:
```bash
psql "postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
```

**Conectar via Python**:
```python
import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM shelly_power_readings")
print(cursor.fetchone())

conn.close()
```

**Adicionar Coluna**:
```sql
ALTER TABLE shelly_power_readings
ADD COLUMN temperatura_c REAL;
```

**Criar Índice**:
```sql
CREATE INDEX idx_power_timestamp
ON shelly_power_readings(power_w, timestamp);
```

### 5. Migrar Dados do InfluxDB

**Script**: `/root/shelly-collector-railway/migrate_influx_to_postgres.py`

```bash
# Configurar variáveis
export INFLUX_URL="https://us-east-1-1.aws.cloud2.influxdata.com"
export INFLUX_ORG="MÁRCIOV ÁRIOSPRO"
export INFLUX_TOKEN="rE69yYhRgXAzF0X7D37zkScPe_-ft1eWNUrmHTFFOoJc_lexGom5fFHsk-07eWxAztvBeOpcpN8Dpt7JyIdouw=="
export INFLUX_BUCKET="energy"
export DATABASE_URL="postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
export MIGRATION_DAYS="30"

# Executar migração
python3 migrate_influx_to_postgres.py
```

**Output Esperado**:
```
======================================================================
📦 Migração: InfluxDB → PostgreSQL
======================================================================
Período: Últimos 30 dias
======================================================================
Conectando ao InfluxDB...
Conectando ao PostgreSQL...
Buscando dados de potência total (últimos 30 dias)...
✓ Obtidos 1234 registos de potência total
✓ Migrados 1234 registos de potência total
Buscando dados por fase (últimos 30 dias)...
✓ Obtidos 3702 registos de fases
✓ Migrados 3702 registos de fases
======================================================================
✅ Migração completa: 4936 registos
======================================================================
```

---

## 🔧 TROUBLESHOOTING

### Problema: Grafana Não Aceita Credenciais

**Sintoma**: 401 Unauthorized ao fazer login

**Causa**: Volume persistente com credenciais antigas

**Solução**:
```python
import requests

# 1. Obter Volume ID
query = """
query {
  service(id: "SERVICE_ID") {
    volumes {
      edges {
        node {
          id
          name
          mountPath
        }
      }
    }
  }
}
"""

# 2. Apagar Volume
mutation = """
mutation {
  volumeDelete(volumeId: "VOLUME_ID")
}
"""

# 3. Ativar acesso anónimo (Railway → Variables)
GF_AUTH_ANONYMOUS_ENABLED=true
GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
```

### Problema: PostgreSQL Connection Timeout

**Sintoma**: `server closed the connection unexpectedly`

**Solução**: Adicionar `?sslmode=require` ao connection string
```python
DATABASE_URL = "postgresql://...?sslmode=require"
```

### Problema: Shelly Não Responde

**Sintoma**: `requests.exceptions.ConnectionError`

**Verificações**:
```bash
# 1. Ping ao Shelly
ping 192.168.0.245

# 2. Testar endpoint
curl http://192.168.0.245/rpc/EM.GetStatus?id=0

# 3. Verificar se está na mesma rede
# Se collector no Railway, precisa VPN (Tailscale) ou proxy
```

### Problema: Tabela Não Existe

**Sintoma**: `relation "shelly_power_readings" does not exist`

**Solução**: Executar create tables
```python
from collect_shelly_postgres import ShellyCollector

collector = ShellyCollector()
collector.create_tables()
```

### Problema: Dashboard Vazio no Grafana

**Verificações**:
1. **Datasource correto?**
   ```sql
   -- Na base de dados correta?
   SELECT COUNT(*) FROM shelly_power_readings;
   ```

2. **Query correta?**
   - Ir ao panel → Edit
   - Ver query SQL
   - Testar manualmente no PostgreSQL

3. **Time range correto?**
   - Verificar se há dados no período selecionado
   - Tentar "Last 7 days" ou "Last 30 days"

---

## 📦 FICHEIROS IMPORTANTES

### `/root/shelly-collector-railway/`
```
collect_shelly_postgres.py    # Worker principal (Railway)
migrate_influx_to_postgres.py # Migração única InfluxDB → PostgreSQL
requirements.txt              # Dependências Python
runtime.txt                   # Versão Python (3.11.7)
Procfile                      # Railway config (worker)
README.md                     # Documentação técnica
.gitignore                    # Ficheiros a ignorar
```

### `/root/shelly-grafana-setup/`
```
docker-compose.yml            # Grafana local (iMac) - OBSOLETO
dashboard-fixed.json          # Dashboard exportado
provisioning/                 # Configs datasource/dashboards
```

---

## 🎯 PRÓXIMOS PASSOS

### Tarefas Pendentes

1. **Deploy do Collector no Railway**
   - [ ] Push código para GitHub
   - [ ] Configurar variáveis de ambiente
   - [ ] Resolver acesso ao Shelly (192.168.0.245)
     - Opção A: Tailscale
     - Opção B: Cloudflare Tunnel
     - Opção C: Proxy local

2. **Atualizar Flask API**
   - [ ] Modificar queries para ler do PostgreSQL
   - [ ] Testar endpoints
   - [ ] Atualizar documentação

3. **Limpar Serviços Desnecessários**
   - [ ] Apagar `shelly-sync-railway` (obsoleto)
   - [ ] Desativar InfluxDB Cloud (após confirmar dados)
   - [ ] Parar Grafana local no iMac

4. **Testes Finais**
   - [ ] Verificar coleta a cada 60s
   - [ ] Confirmar dados no Grafana
   - [ ] Testar API endpoints
   - [ ] Monitorizar durante 24h

---

## 📞 COMANDOS RÁPIDOS

### Ver Dados no PostgreSQL
```bash
psql "postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require" -c "SELECT COUNT(*) FROM shelly_power_readings;"
```

### Testar Shelly
```bash
curl http://192.168.0.245/rpc/EM.GetStatus?id=0 | jq .
```

### Executar Collector Localmente
```bash
cd /root/shelly-collector-railway
export SHELLY_IP="192.168.0.245"
export DATABASE_URL="postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
python3 collect_shelly_postgres.py
```

### Aceder ao Grafana
```bash
# Abrir no browser
open https://grafana-production-db87.up.railway.app/
```

---

**Última Atualização**: 2026-01-13
**Criado por**: Márcio Miguel + Claude
**Versão**: 1.0
