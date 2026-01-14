# 🔌 Shelly Pro 3EM → PostgreSQL Collector

**Worker para Railway - Arquitetura PostgreSQL Only**

Coleta dados direto do Shelly Pro 3EM e guarda no PostgreSQL Railway, eliminando dependência do iMac e InfluxDB.

---

## 📋 O Que Faz

```
Shelly Pro 3EM (LAN)
    ↓ HTTP Request a cada 60s
collector-railway (Railway Worker)
    ↓ INSERT PostgreSQL
PostgreSQL Railway
    ↓
    ├─→ shelly-api-railway (Flask)
    └─→ Grafana Railway
```

---

## 🚀 Deploy no Railway

### 1. Criar Repositório GitHub

```bash
cd /root/shelly-collector-railway
git init
git add .
git commit -m "Initial commit: Shelly PostgreSQL collector"
git branch -M main
git remote add origin https://github.com/MarcioMiguel22/shelly-collector-railway.git
git push -u origin main
```

### 2. Deploy no Railway

1. Vai a https://railway.app/new
2. **Deploy from GitHub repo**
3. Seleciona `shelly-collector-railway`
4. Railway faz deploy automático

### 3. Configurar Variáveis

No Railway → **Variables**:

```bash
# IP do Shelly na tua rede local
SHELLY_IP=192.168.0.245

# PostgreSQL (Railway fornece automaticamente)
DATABASE_URL=postgresql://...

# Intervalo de coleta (opcional, default 60s)
COLLECTION_INTERVAL=60
```

**IMPORTANTE**: O Railway precisa conseguir aceder ao IP `192.168.0.245`. Isto só funciona se:
- Railway estiver na mesma VPN/rede (Tailscale, Cloudflare Tunnel, etc.)
- OU usar um proxy/bridge na tua rede local

### 4. Configurar Acesso ao Shelly

**Opção A: Usar Tailscale (RECOMENDADO)**

1. Instala Tailscale no Railway (via Railway Template)
2. Conecta à tua Tailnet
3. O Shelly fica acessível via IP Tailscale

**Opção B: Cloudflare Tunnel**

1. Cria tunnel para tua rede local
2. Expõe Shelly via tunnel
3. Usa URL do tunnel em `SHELLY_IP`

**Opção C: Manter no iMac (Temporário)**

Se preferires manter coleta no iMac temporariamente:
```bash
# No iMac
cd /root/shelly-collector-railway
python3 collect_shelly_postgres.py
```

---

## 📊 Tabelas PostgreSQL

### `shelly_power_readings`
Leituras de potência (total + por fase)

### `shelly_phase_data`
Dados detalhados por fase (potência reativa, aparente, etc.)

### `shelly_energy_summary`
Resumos de energia acumulada

### `shelly_device_info`
Informações do dispositivo

---

## 🧪 Testar Localmente

```bash
export SHELLY_IP="192.168.0.245"
export DATABASE_URL="postgresql://postgres:password@localhost/railway"
export COLLECTION_INTERVAL="60"

python3 collect_shelly_postgres.py
```

---

## ✅ Vantagens desta Arquitetura

- ✅ **Sem InfluxDB** - 1 base de dados só
- ✅ **Sem dependência do iMac** (com Tailscale/Tunnel)
- ✅ **Grafana funcional** - Já configurado
- ✅ **API continua a funcionar** - Lê do PostgreSQL
- ✅ **Simples e barato** - €0-5/mês

---

## 📦 Próximos Passos

Depois do deploy:

1. ✅ Verificar logs no Railway
2. ✅ Confirmar dados a chegar no PostgreSQL
3. ✅ Atualizar API Flask para ler do PostgreSQL
4. ✅ Testar Grafana com dados reais
5. ✅ Desligar iMac (se usar Tailscale)

---

**Criado por:** Márcio Miguel + Claude
**Data:** 2026-01-13
