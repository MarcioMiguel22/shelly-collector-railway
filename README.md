# ⚡ Shelly Pro 3EM → PostgreSQL Collector

[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-blueviolet)](https://railway.app/new/template)
[![Python](https://img.shields.io/badge/Python-3.11.7-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Worker automático para Railway** que coleta dados elétricos do Shelly Pro 3EM e armazena no PostgreSQL.

Monitoriza potência, corrente, tensão, fator de potência e frequência em tempo real, com visualização no Grafana.

---

## ✨ Features

- ✅ **Coleta automática a cada 60s** do Shelly Pro 3EM
- ✅ **PostgreSQL Railway** como única base de dados
- ✅ **Métricas completas**: Potência, Corrente, Tensão, Fator de Potência, Frequência
- ✅ **3 fases + total** (A, B, C)
- ✅ **Grafana Dashboard** incluído
- ✅ **Zero dependências** de servidores locais (com Tailscale/Tunnel)
- ✅ **Migration tool** do InfluxDB incluída

---

## 📊 Arquitetura

```
Shelly Pro 3EM (192.168.0.245)
    ↓ HTTP GET a cada 60s
Railway Worker (collect_shelly_postgres.py)
    ↓ INSERT INTO PostgreSQL
PostgreSQL Railway
    ↓
    ├─→ Grafana Railway (Visualização)
    └─→ Flask API (Acesso via REST)
```

**Sem InfluxDB. Sem iMac. PostgreSQL Only.**

---

## 🚀 Deploy Rápido

### Passo 1: Fork/Clone este repo

```bash
git clone https://github.com/MarcioMiguel22/shelly-collector-railway.git
cd shelly-collector-railway
```

### Passo 2: Deploy no Railway

1. Vai a **https://railway.app/**
2. **New Project** → **Deploy from GitHub repo**
3. Seleciona **shelly-collector-railway**
4. Railway detecta automaticamente o `Procfile` e `runtime.txt`

### Passo 3: Configurar Variáveis

No Railway → **Variables**:

```bash
# PostgreSQL (usa referência automática do Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# IP do Shelly (ver nota abaixo sobre acesso à rede)
SHELLY_IP=192.168.0.245

# Intervalo de coleta (opcional)
COLLECTION_INTERVAL=60
```

### Passo 4: ⚠️ Resolver Acesso ao Shelly

O Shelly está na tua rede local. Escolhe uma opção:

| Opção | Complexidade | Recomendado para |
|-------|--------------|------------------|
| **Tailscale** | Média | Produção |
| **Cloudflare Tunnel** | Média | Produção alternativa |
| **Executar localmente** | Baixa | Teste/Temporário |

📖 **Ver guia completo**: [DEPLOY_RAILWAY_GUIDE.md](DEPLOY_RAILWAY_GUIDE.md)

---

## 📊 Dados Coletados

O collector guarda dados em **4 tabelas PostgreSQL**:

### `shelly_power_readings` (Principal)
Leituras de potência, corrente, tensão, fator de potência e frequência.
- Total + 3 fases (A, B, C)
- Atualizado a cada 60s
- Índices otimizados para queries temporais

### `shelly_phase_data` (Detalhado)
Potência ativa, reativa, aparente por fase.

### `shelly_energy_summary` (Acumulado)
Energia total consumida/retornada.

### `shelly_device_info` (Status)
Firmware, uptime, temperatura, WiFi RSSI.

---

## 📈 Grafana Dashboard

Dashboard completo incluído: **⚡ Shelly Pro 3EM - Monitor Completo**

**Métricas visualizadas**:
- 🔌 Potência TOTAL + por fase (W)
- ⚡ Corrente TOTAL + por fase (A)
- 🔋 Tensão média + por fase (V)
- 📐 Fator de potência por fase
- 🌊 Frequência da rede (Hz)
- 📋 Tabela com últimas 50 leituras

**Cores por fase**: A=🔴 Vermelho | B=🟡 Amarelo | C=🔵 Azul

---

## 🧪 Testar Localmente

```bash
# Clonar e configurar
git clone https://github.com/MarcioMiguel22/shelly-collector-railway.git
cd shelly-collector-railway

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
export SHELLY_IP="192.168.0.245"
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Executar
python3 collect_shelly_postgres.py
```

**Output esperado**:
```
🔌 Shelly Pro 3EM → PostgreSQL Collector
Shelly IP: 192.168.0.245
PostgreSQL: host:port/db
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly
✓ Guardados 4 readings + 3 phase data (Total: 245.32W)
```

---

## 🗂️ Estrutura do Projeto

```
shelly-collector-railway/
├── collect_shelly_postgres.py    # Worker principal
├── migrate_influx_to_postgres.py # Migration tool (InfluxDB → PostgreSQL)
├── requirements.txt               # Dependências Python
├── runtime.txt                    # Python 3.11.7
├── Procfile                       # Railway worker config
├── README.md                      # Este ficheiro
├── DEPLOY_RAILWAY_GUIDE.md        # Guia de deploy detalhado
└── CEREBRO_SISTEMA_SHELLY_RAILWAY.md  # Documentação técnica completa
```

---

## 🔧 Migration do InfluxDB

Se tens dados históricos no InfluxDB Cloud:

```bash
# Configurar variáveis
export INFLUX_URL="https://us-east-1-1.aws.cloud2.influxdata.com"
export INFLUX_ORG="TUA_ORG"
export INFLUX_TOKEN="TUA_TOKEN"
export INFLUX_BUCKET="energy"
export DATABASE_URL="postgresql://..."
export MIGRATION_DAYS="30"  # Quantos dias migrar

# Executar migração
python3 migrate_influx_to_postgres.py
```

---

## 📖 Documentação

- **[DEPLOY_RAILWAY_GUIDE.md](DEPLOY_RAILWAY_GUIDE.md)** - Guia completo de deploy
- **[CEREBRO_SISTEMA_SHELLY_RAILWAY.md](CEREBRO_SISTEMA_SHELLY_RAILWAY.md)** - Documentação técnica (credenciais, queries, troubleshooting)

---

## 🎯 Próximos Passos

Depois do deploy bem-sucedido:

1. ✅ Verificar logs no Railway
2. ✅ Confirmar dados completos no PostgreSQL (corrente, tensão, etc.)
3. ✅ Abrir Grafana e verificar dashboard
4. ✅ Migrar dados históricos do InfluxDB (opcional)
5. ✅ Desativar InfluxDB Cloud
6. ✅ Desligar coleta local (se aplicável)

---

## 💰 Custo

- **Railway Free Tier**: $5 créditos/mês
- **Este setup**: ~€0-2/mês (Worker + PostgreSQL)
- **InfluxDB eliminado**: -€0 (já não é necessário)

**Total**: Praticamente grátis! 🎉

---

## 📝 License

MIT License - Usa à vontade!

---

**Criado por:** Márcio Miguel + Claude
**Data:** 2026-01-14
**Repositório:** https://github.com/MarcioMiguel22/shelly-collector-railway
