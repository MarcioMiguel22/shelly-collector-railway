# 🚀 DEPLOY AGORA - Guia Ultra-Rápido

**Repositório pronto**: https://github.com/MarcioMiguel22/shelly-collector-railway

---

## ⚡ 3 PASSOS RÁPIDOS

### 1️⃣ Criar Serviço no Railway

1. Abre **https://railway.app/**
2. Faz login (se necessário)
3. Abre o projeto onde tens o **Grafana** e **PostgreSQL**
4. Clica **+ New**
5. Seleciona **GitHub Repo**
6. Procura **shelly-collector-railway**
7. Clica **Deploy Now**

Railway vai:
- ✅ Detectar `Procfile` (worker)
- ✅ Detectar `runtime.txt` (Python 3.11.7)
- ✅ Instalar `requirements.txt`
- ✅ Iniciar deploy

---

### 2️⃣ Configurar Variáveis

Depois do deploy inicial:

1. Clica no serviço **shelly-collector**
2. Vai a **Variables**
3. Adiciona estas 2 variáveis:

```bash
DATABASE_URL
```
**Valor**: Clica em **Add Reference** → Seleciona o teu **PostgreSQL** → `DATABASE_URL`

```bash
SHELLY_IP
```
**Valor**: `192.168.0.245` (ou IP Tailscale se configuraste)

```bash
COLLECTION_INTERVAL
```
**Valor**: `60` (opcional, 60s é o default)

4. Clica **Deploy** (Railway vai reiniciar com as novas variáveis)

---

### 3️⃣ Verificar Logs

1. No serviço **shelly-collector**
2. Vai a **Deployments**
3. Clica no último deployment
4. Clica **View Logs**

**✅ SE FUNCIONAR, vais ver**:
```
🔌 Shelly Pro 3EM → PostgreSQL Collector
Shelly IP: 192.168.0.245
PostgreSQL: tramway.proxy.rlwy.net:46128/railway
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly (192.168.0.245)
✓ Guardados 4 readings + 3 phase data (Total: 245.32W)
Próxima coleta em 60s...
```

**❌ SE DER ERRO de conexão ao Shelly**:
```
Erro ao buscar dados do Shelly: HTTPConnectionPool...
```

→ **Normal!** Railway não consegue aceder a `192.168.0.245` (é rede local).

---

## 🔧 RESOLVER ERRO DE REDE

Se der erro de conexão ao Shelly, tens **3 opções**:

### 🏆 Opção 1: Tailscale (Recomendado)

**Vantagem**: Melhor solução para produção

1. No Railway, clica **+ New** → **Template**
2. Procura "**Tailscale**"
3. Deploy do template
4. Vai a https://login.tailscale.com/admin/settings/keys
5. Cria **Auth Key**
6. Adiciona variável `TAILSCALE_AUTHKEY` no serviço Tailscale
7. Instala Tailscale no teu router/servidor local
8. Atualiza `SHELLY_IP` para o IP Tailscale (ex: `100.x.x.x`)

**Tempo**: ~15 minutos

---

### 🌐 Opção 2: Cloudflare Tunnel

**Vantagem**: Não precisa VPN

1. Instala cloudflared no teu servidor local
2. Cria tunnel: `cloudflared tunnel create shelly`
3. Configura para expor Shelly
4. Atualiza `SHELLY_IP` para URL do tunnel

**Tempo**: ~10 minutos

---

### 💻 Opção 3: Executar Localmente (Temporário)

**Vantagem**: Funciona imediatamente

No teu iMac/servidor local:

```bash
cd /root/shelly-collector-railway

# Configurar
export SHELLY_IP="192.168.0.245"
export DATABASE_URL="postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
export COLLECTION_INTERVAL="60"

# Executar
python3 collect_shelly_postgres.py
```

**Desvantagem**: Depende do iMac/servidor estar sempre ligado.

---

## ✅ VERIFICAR SE ESTÁ A FUNCIONAR

### 1. Ver dados no PostgreSQL

```bash
psql "postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
```

```sql
-- Ver últimas leituras
SELECT * FROM shelly_power_readings
ORDER BY timestamp DESC
LIMIT 10;

-- Verificar se tem TODOS os dados (não só power_w)
SELECT
    timestamp,
    phase,
    power_w,
    current_a,    -- Deve ter valor!
    voltage_v,    -- Deve ter valor!
    power_factor, -- Deve ter valor!
    frequency_hz  -- Deve ter valor!
FROM shelly_power_readings
WHERE timestamp > NOW() - INTERVAL '5 minutes'
ORDER BY timestamp DESC;
```

**✅ Se `current_a`, `voltage_v`, etc. tiverem valores**: Está tudo a funcionar!

---

### 2. Ver no Grafana

1. Abre **https://grafana-production-db87.up.railway.app/d/shelly-3em-completo/**
2. Verifica se os painéis mostram dados:
   - ✅ Potência TOTAL Atual
   - ✅ Corrente TOTAL Atual
   - ✅ Tensão Média
   - ✅ Frequência
   - ✅ Gráficos de potência por fase

**⏱️ NOTA**: Dados novos (com corrente, tensão, etc.) só aparecem DEPOIS de o collector começar a funcionar!

---

## 🎯 RESULTADO ESPERADO

Depois de tudo configurado:

1. ✅ **Railway Worker** a correr 24/7
2. ✅ **Coleta automática** a cada 60s
3. ✅ **PostgreSQL** com TODOS os dados:
   - Potência (W)
   - Corrente (A)
   - Tensão (V)
   - Fator de Potência
   - Frequência (Hz)
4. ✅ **Grafana Dashboard** com visualizações completas
5. ✅ **Zero dependências** do iMac (se usares Tailscale/Tunnel)

---

## 📞 PROBLEMAS?

Consulta a documentação completa:
- **[DEPLOY_RAILWAY_GUIDE.md](DEPLOY_RAILWAY_GUIDE.md)** - Guia detalhado com troubleshooting
- **[CEREBRO_SISTEMA_SHELLY_RAILWAY.md](CEREBRO_SISTEMA_SHELLY_RAILWAY.md)** - Documentação técnica completa

---

**Boa sorte! 🚀**

---

**Criado por:** Márcio Miguel + Claude
**Data:** 2026-01-14
