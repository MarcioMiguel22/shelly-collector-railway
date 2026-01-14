# 🚀 DEPLOY NO RAILWAY - INSTRUÇÕES FINAIS

**TUDO JÁ ESTÁ PRONTO!** Só precisas de fazer deploy no Railway.

---

## ✅ O QUE JÁ ESTÁ FEITO

- ✅ Código no GitHub: https://github.com/MarcioMiguel22/shelly-collector-railway
- ✅ `Procfile` atualizado para usar Cloud API
- ✅ Credenciais Shelly Cloud obtidas
- ✅ Dashboard Grafana configurado

---

## 🚀 DEPLOY NO RAILWAY (5 MINUTOS)

### PASSO 1: Criar Serviço

1. Vai a **https://railway.app/**
2. Faz login (se necessário)
3. Abre o projeto onde tens **Grafana** e **PostgreSQL**
4. Clica **+ New**
5. Seleciona **GitHub Repo**
6. Procura e seleciona: **shelly-collector-railway**
7. Clica **Deploy**

Railway vai começar o deploy automático!

---

### PASSO 2: Configurar Variáveis

Enquanto faz deploy, configura as variáveis:

1. No serviço que acabou de criar, clica em **Variables**
2. Adiciona estas **5 variáveis**:

#### Variável 1: DATABASE_URL

- Clica **+ New Variable**
- Clica **Add Reference**
- Seleciona o serviço **PostgreSQL** (postgres)
- Seleciona a variável **DATABASE_URL**
- Clica **Add**

#### Variável 2: SHELLY_CLOUD_SERVER

- Clica **+ New Variable**
- **Name**: `SHELLY_CLOUD_SERVER`
- **Value**: `shelly-174-eu.shelly.cloud`
- Clica **Add**

#### Variável 3: SHELLY_AUTH_KEY

- Clica **+ New Variable**
- **Name**: `SHELLY_AUTH_KEY`
- **Value**: `MmZjYzUydWlk115BA0F7C6074DEB3670AF7C65E406739E70D8FC9B71463C1C077EF4AECF12FCBB490A77E632D443`
- Clica **Add**

#### Variável 4: SHELLY_DEVICE_ID

- Clica **+ New Variable**
- **Name**: `SHELLY_DEVICE_ID`
- **Value**: `3030f9ec66ac`
- Clica **Add**

#### Variável 5: COLLECTION_INTERVAL

- Clica **+ New Variable**
- **Name**: `COLLECTION_INTERVAL`
- **Value**: `60`
- Clica **Add**

---

### PASSO 3: Redeploy (se necessário)

Se o deploy já acabou antes de configurares as variáveis:

1. Vai a **Deployments**
2. Clica nos **3 pontos** (⋮) do último deployment
3. Clica **Redeploy**

Railway vai reiniciar com as variáveis configuradas!

---

## ✅ VERIFICAR SE ESTÁ A FUNCIONAR

### 1. Ver Logs

1. No Railway, clica no serviço **shelly-collector-railway**
2. Vai a **Deployments**
3. Clica no deployment ativo (verde)
4. Clica **View Logs**

**Deve aparecer:**

```
🌐 Shelly Pro 3EM → PostgreSQL Collector (Cloud API)
======================================================================
Shelly Cloud: shelly-174-eu.shelly.cloud
Device ID: 3030f9ec66ac
Intervalo de coleta: 60s
Pressiona Ctrl+C para parar
======================================================================
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 245.32W)
Próxima coleta em 60s...

--- Coleta #2 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 238.15W)
Próxima coleta em 60s...
```

**✅ SE VIRES ISTO** → Está tudo a funcionar perfeitamente!

**❌ SE HOUVER ERROS:**

- `Auth Key inválida` → Verifica se copiaste a key completa
- `Device ID não encontrado` → Verifica se o ID está correto
- `Cannot connect to database` → Verifica se DATABASE_URL está como referência

---

### 2. Verificar Dados no PostgreSQL

Podes testar a conexão diretamente:

```bash
psql "postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
```

Depois executa:

```sql
SELECT
    timestamp,
    phase,
    ROUND(power_w::numeric, 1) as power_w,
    ROUND(current_a::numeric, 2) as current_a,
    ROUND(voltage_v::numeric, 1) as voltage_v
FROM shelly_power_readings
WHERE timestamp > NOW() - INTERVAL '5 minutes'
ORDER BY timestamp DESC
LIMIT 20;
```

**Deve mostrar dados NOVOS** (timestamp recente)!

---

### 3. Ver no Grafana

Abre: **https://grafana-production-db87.up.railway.app/d/shelly-energia/**

**Deve mostrar:**

- ⚡ **POTÊNCIA TOTAL**: Valor atual (ex: 245W)
- 🔴 **FASE A**: Valor atual (ex: 2W)
- 🟡 **FASE B**: Valor atual (ex: 138W)
- 🔵 **FASE C**: Valor atual (ex: 44W)
- 🔥 **Pico Máximo Hoje**: Valor máximo registado
- 📊 **Média Hoje**: Consumo médio
- 📈 **Gráficos**: A atualizar automaticamente

**⏱️ NOTA**: Espera 1-2 minutos após o deploy para os primeiros dados aparecerem!

Se aparecer **"No data"**:
- Espera mais 2-3 minutos
- Faz refresh (Ctrl+Shift+R)
- Verifica os logs do collector

---

## 🎉 PARABÉNS!

### Quando tudo estiver a funcionar:

✅ **Collector a correr 24/7 no Railway**
✅ **Dados via Shelly Cloud** (sem iMac, sem Tailscale)
✅ **PostgreSQL com dados em tempo real**
✅ **Grafana com dashboard atualizado**
✅ **ZERO dependências do iMac**

---

## 🧹 LIMPEZA DO iMac (OPCIONAL)

Depois de confirmar que tudo funciona no Railway, podes limpar o iMac:

```bash
# Parar collector local (se estiver a correr)
pkill -f collect_shelly_postgres.py

# Parar Grafana local
cd /root/shelly-grafana-setup
docker-compose down

# Remover volumes do Grafana (liberta espaço)
docker volume rm shelly-grafana-setup_grafana-data
```

---

## 💰 CUSTO FINAL

- **Railway Worker** (Collector): ~€1/mês
- **PostgreSQL Railway**: ~€1/mês
- **Grafana Railway**: €0 (incluído)
- **Shelly Cloud**: €0 (grátis)

**Total: ~€2/mês** 🎉

---

## 📊 RESUMO DAS CREDENCIAIS

**Shelly Cloud:**
- Server: `shelly-174-eu.shelly.cloud`
- Auth Key: `MmZjYzUy...` (guardado)
- Device ID: `3030f9ec66ac`

**PostgreSQL Railway:**
- Host: `tramway.proxy.rlwy.net:46128`
- Database: `railway`
- User: `postgres`
- Password: `RFVUeMxciMxzOFmwucLcDYqovaPEBEDb`

**Grafana Railway:**
- URL: https://grafana-production-db87.up.railway.app/
- Dashboard: https://grafana-production-db87.up.railway.app/d/shelly-energia/
- Acesso: Anónimo (Admin)

---

## 🔧 TROUBLESHOOTING

### Logs mostram "Erro ao buscar dados do Shelly Cloud"

**Possíveis causas:**
1. Auth Key incorreta → Verifica se copiaste completa
2. Device ID errado → Confirma na app Shelly
3. Servidor errado → Deve ser `shelly-174-eu.shelly.cloud`
4. Shelly offline → Verifica na app se está online

**Solução:**
- Vai às **Variables** no Railway
- Corrige a variável incorreta
- Serviço reinicia automaticamente

### Dashboard mostra "No data"

**Espera 2-3 minutos** após o deploy!

Se continuar:
1. Verifica logs do collector (deve mostrar "✓ Guardados")
2. Testa query SQL no PostgreSQL
3. Faz hard refresh no Grafana (Ctrl+Shift+R)

### Collector para de funcionar

1. Vai a **Deployments** no Railway
2. Verifica se há erros nos logs
3. Se necessário, faz **Redeploy**

---

## 📞 AJUDA

Toda a documentação está em:
- **GitHub**: https://github.com/MarcioMiguel22/shelly-collector-railway
- **COMO_USAR_SHELLY_CLOUD.md** - Guia Cloud API
- **CEREBRO_SISTEMA_SHELLY_RAILWAY.md** - Referência técnica

---

**BOA SORTE! 🚀**

**Tempo estimado**: 5-10 minutos
**Dificuldade**: Fácil ⭐
**Resultado**: Sistema 100% cloud! 🎉
