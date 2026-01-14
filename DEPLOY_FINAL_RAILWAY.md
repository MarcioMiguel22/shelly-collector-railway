# 🚀 Deploy Final no Railway - 3 Passos Simples

**Objetivo**: Tudo a funcionar no Railway, ZERO dependências do iMac

---

## 📱 PASSO 1: Obter Credenciais Shelly Cloud (2 minutos)

O teu Shelly Pro 3EM provavelmente JÁ está conectado ao Shelly Cloud.

### Como verificar:

1. Abre **Shelly Smart Control** app no telemóvel
2. Vês o Shelly Pro 3EM listado?
   - **SIM** → Está no cloud! Continua ✅
   - **NÃO** → Precisas configurar cloud primeiro

### Obter Auth Key e Device ID:

**Na App Shelly Smart Control:**

1. Abre o app
2. Vai a **User** (ícone de perfil) → **Cloud**
3. Anota o **Server**: (ex: `shelly-13-eu.shelly.cloud`)
4. Procura **Authorization Key** ou **Server Key**
   - Copia essa key (longa string)
5. Volta atrás, abre o **Shelly Pro 3EM**
6. Vai a ⚙️ **Settings** → **Device Information**
7. Copia o **Device ID** (ex: `shellyem3-C45BBE7A1234`)

**Anota:**
- Server: `_________________`
- Auth Key: `_________________`
- Device ID: `_________________`

---

## 🌐 PASSO 2: Deploy no Railway (5 minutos)

### 2.1 Criar Serviço

1. Vai a **https://railway.app/**
2. Abre o projeto onde tens **Grafana** e **PostgreSQL**
3. Clica **+ New**
4. Seleciona **GitHub Repo**
5. Escolhe **shelly-collector-railway**
6. Railway começa a fazer deploy

### 2.2 Configurar Variáveis

No serviço **shelly-collector-railway** → **Variables**:

Adiciona estas 5 variáveis:

```bash
DATABASE_URL
```
**Valor**: Clica em **+ New Variable** → **Add Reference** → Seleciona o teu **PostgreSQL** → `DATABASE_URL`

```bash
SHELLY_CLOUD_SERVER
```
**Valor**: `shelly-13-eu.shelly.cloud` (ou o server que anotaste)

```bash
SHELLY_AUTH_KEY
```
**Valor**: Cola a auth key que copiaste

```bash
SHELLY_DEVICE_ID
```
**Valor**: Cola o device ID (ex: `shellyem3-C45BBE7A1234`)

```bash
COLLECTION_INTERVAL
```
**Valor**: `60` (coleta a cada 60 segundos)

### 2.3 Mudar para Cloud API

**IMPORTANTE**: Por default usa API local. Para usar Cloud:

No GitHub, edita o ficheiro `Procfile`:

**ANTES:**
```
worker: python collect_shelly_postgres.py
```

**DEPOIS:**
```
worker: python collect_shelly_cloud.py
```

**Como fazer:**

```bash
cd /root/shelly-collector-railway

# Editar Procfile
echo "worker: python collect_shelly_cloud.py" > Procfile

# Commit e push
git add Procfile
git commit -m "Switch to Shelly Cloud API"
git push
```

Railway vai fazer **redeploy automático**!

---

## ✅ PASSO 3: Verificar (2 minutos)

### 3.1 Ver Logs

No Railway:
1. Vai ao serviço **shelly-collector-railway**
2. Clica em **Deployments**
3. Clica no deployment mais recente
4. Clica em **View Logs**

**Deve aparecer:**
```
🌐 Shelly Pro 3EM → PostgreSQL Collector (Cloud API)
Shelly Cloud: shelly-13-eu.shelly.cloud
Device ID: shellyem3-C45BBE7A1234
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 245.32W)
Próxima coleta em 60s...

--- Coleta #2 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 238.15W)
```

### 3.2 Verificar PostgreSQL

Abre qualquer SQL client e conecta:

```
Host: tramway.proxy.rlwy.net
Port: 46128
Database: railway
User: postgres
Password: RFVUeMxciMxzOFmwucLcDYqovaPEBEDb
```

Executa:
```sql
SELECT
    timestamp,
    phase,
    power_w,
    current_a,
    voltage_v
FROM shelly_power_readings
WHERE timestamp > NOW() - INTERVAL '5 minutes'
ORDER BY timestamp DESC;
```

**Deve mostrar dados NOVOS** (timestamp recente)!

### 3.3 Verificar Grafana

Abre: https://grafana-production-db87.up.railway.app/d/shelly-energia/

**Deve mostrar:**
- ⚡ **Potência TOTAL Atual**: Valor atual
- 🔴🟡🔵 **Fases A, B, C**: Valores atualizados
- 🔥 **Pico Máximo Hoje**: Valor correto
- 📈 **Gráficos**: A atualizar em tempo real

Se vires **"No data"** → Espera 2-3 minutos para dados chegarem!

---

## 🎉 PRONTO!

### ✅ O que tens agora:

- ✅ **Collector a correr 24/7 no Railway** (sem iMac)
- ✅ **Dados a chegar via Shelly Cloud** (sem Tailscale)
- ✅ **PostgreSQL Railway** com dados em tempo real
- ✅ **Grafana Railway** com dashboard atualizado
- ✅ **ZERO dependências** do iMac

### 💰 Custo:

- Railway: ~€2/mês (Worker + PostgreSQL)
- Shelly Cloud: Grátis
- **Total: €2/mês**

---

## 🧹 LIMPEZA (Opcional)

Depois de confirmar que tudo funciona:

### No iMac:

```bash
# Parar collector local (se estiver a correr)
pkill -f collect_shelly_postgres.py

# Parar Grafana local
cd /root/shelly-grafana-setup
docker-compose down
```

### No Railway:

1. Apagar serviço **shelly-sync-railway** (obsoleto)
2. Remover PostgreSQL antigo **switchback** (se não for usado)

### InfluxDB Cloud:

1. Vai a https://cloud2.influxdata.com/
2. Apaga o bucket **energy** (dados já migrados)
3. Cancela subscrição (se aplicável)

---

## 🔧 TROUBLESHOOTING

### Erro: "Auth Key inválida"

1. Verifica que copiaste a key completa (sem espaços)
2. Gera nova key no Shelly Cloud
3. Atualiza variável `SHELLY_AUTH_KEY` no Railway

### Erro: "Device ID não encontrado"

1. Confirma o ID na app (deve começar com `shelly`)
2. Verifica que o dispositivo está **online** no cloud
3. Testa na app se consegues ver dados em tempo real

### Erro: "Cannot connect to database"

1. Verifica que `DATABASE_URL` está configurado como **referência**
2. Confirma que PostgreSQL está ativo no Railway
3. Testa conexão manualmente

### Dashboard mostra "No data"

1. Espera 2-3 minutos (coleta inicial)
2. Verifica logs do collector (deve mostrar "✓ Guardados...")
3. Confirma que há dados no PostgreSQL (query acima)
4. Faz refresh do Grafana (Ctrl+Shift+R)

---

## 📞 AJUDA

Se alguma coisa não funcionar:

1. **Ver logs** do collector no Railway
2. **Testar** conexão ao cloud manualmente (via app)
3. **Verificar** se variáveis estão corretas

Toda a documentação está em:
- **COMO_USAR_SHELLY_CLOUD.md** - Guia detalhado Cloud API
- **CEREBRO_SISTEMA_SHELLY_RAILWAY.md** - Referência técnica completa

---

**Boa sorte! 🚀**

**Tempo total**: ~10 minutos
**Dificuldade**: Fácil ⭐
**Resultado**: Sistema 100% cloud, sem iMac! 🎉
