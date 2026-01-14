# 🎯 DEPLOY MANUAL - PASSO A PASSO COM SCREENSHOTS MENTAIS

**A API do Railway está com problemas. Vou guiar-te manualmente (5 minutos).**

---

## 🚀 PASSO-A-PASSO VISUAL

### 📍 PASSO 1: Abrir Railway (10 segundos)

1. Abre browser
2. Vai a: **https://railway.app/**
3. Faz login (se necessário)
4. Vês a lista de projetos

---

### 📍 PASSO 2: Abrir Projeto Correto (10 segundos)

**Procura e clica no projeto**: **"Password + PaginasVarias"**

(É o que tem Grafana, PostgreSQL, Redis, etc.)

---

### 📍 PASSO 3: Adicionar Novo Serviço (30 segundos)

1. **Dentro do projeto**, vês vários "cards" (Grafana, Postgres, Redis, etc.)

2. Clica no botão **"+ New"** (canto superior direito ou centro)

3. Aparece menu com opções:
   - Empty Service
   - **GitHub Repo** ← **CLICA AQUI**
   - Database
   - Template

4. Vai aparecer lista dos teus repositórios GitHub

5. **Procura**: `shelly-collector-railway`

6. **Clica nele**

7. Railway começa a fazer deploy automático!
   - Vês barra de progresso
   - Logs a aparecer
   - Status: "Building..."

---

### 📍 PASSO 4: Configurar Variáveis (2 minutos)

Enquanto faz build, vamos configurar as variáveis:

1. **Clica no card** do serviço que acabou de criar
   (deve dizer "shelly-collector-railway" ou similar)

2. Vê várias tabs:
   - Deployments
   - **Variables** ← **CLICA AQUI**
   - Settings
   - Metrics

3. Agora vais adicionar **5 variáveis**:

---

#### ✅ VARIÁVEL 1: DATABASE_URL (Referência)

1. Clica **"+ New Variable"** ou **"New Variable"**

2. Em vez de escrever, clica em **"Add Reference"** ou ícone de corrente 🔗

3. Aparece dropdown de serviços do projeto

4. Seleciona: **"Postgres"** ou **"Cérebro de Sistemas"** (o PostgreSQL)

5. Aparece nova dropdown de variáveis

6. Seleciona: **"DATABASE_URL"**

7. Clica **"Add"**

✅ Variável adicionada! Vês: `${{Postgres.DATABASE_URL}}`

---

#### ✅ VARIÁVEL 2: SHELLY_CLOUD_SERVER

1. Clica **"+ New Variable"** de novo

2. Desta vez, clica em **"Raw Editor"** ou simplesmente escreve:

   **Name**: `SHELLY_CLOUD_SERVER`

   **Value**: `shelly-174-eu.shelly.cloud`

3. Clica **"Add"** ou pressiona Enter

✅ Adicionada!

---

#### ✅ VARIÁVEL 3: SHELLY_AUTH_KEY

1. **"+ New Variable"**

2. **Name**: `SHELLY_AUTH_KEY`

3. **Value**: `MmZjYzUydWlk115BA0F7C6074DEB3670AF7C65E406739E70D8FC9B71463C1C077EF4AECF12FCBB490A77E632D443`

   (Copia-cola isto completo!)

4. Clica **"Add"**

✅ Adicionada!

---

#### ✅ VARIÁVEL 4: SHELLY_DEVICE_ID

1. **"+ New Variable"**

2. **Name**: `SHELLY_DEVICE_ID`

3. **Value**: `3030f9ec66ac`

4. Clica **"Add"**

✅ Adicionada!

---

#### ✅ VARIÁVEL 5: COLLECTION_INTERVAL

1. **"+ New Variable"**

2. **Name**: `COLLECTION_INTERVAL`

3. **Value**: `60`

4. Clica **"Add"**

✅ Adicionada!

---

### 📍 PASSO 5: Verificar Deploy (1 minuto)

1. Clica na tab **"Deployments"**

2. Vês lista de deployments (pelo menos 1)

3. Clica no deployment mais recente (topo da lista)

4. Vês:
   - Status: "Success" ou "Building" ou "Crashed"
   - Botão **"View Logs"**

5. Clica em **"View Logs"**

---

### 📍 PASSO 6: Ler os Logs (1 minuto)

**SE TUDO CORREU BEM**, vês nos logs:

```
🌐 Shelly Pro 3EM → PostgreSQL Collector (Cloud API)
======================================================================
Shelly Cloud: shelly-174-eu.shelly.cloud
Device ID: 3030f9ec66ac
Intervalo de coleta: 60s
======================================================================
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 245W)
Próxima coleta em 60s...

--- Coleta #2 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 238W)
```

**✅ PERFEITO!** Está a funcionar!

---

**SE HOUVER ERROS**, pode ser:

❌ **"DATABASE_URL não configurado"**
- Volta às Variables
- Confirma que DATABASE_URL está lá como referência

❌ **"Auth Key inválida"**
- Verifica se copiaste a key completa
- Deve ter 88 caracteres

❌ **"Cannot connect to Shelly Cloud"**
- Verifica SHELLY_CLOUD_SERVER
- Deve ser: `shelly-174-eu.shelly.cloud` (sem https://)

❌ **"Device not found"**
- Verifica SHELLY_DEVICE_ID
- Deve ser: `3030f9ec66ac`

**Para corrigir erros:**
1. Vai a **Variables**
2. Corrige a variável errada
3. Serviço reinicia automaticamente
4. Volta aos Logs para verificar

---

### 📍 PASSO 7: Verificar Grafana (30 segundos)

1. Abre novo tab no browser

2. Vai a: **https://grafana-production-db87.up.railway.app/d/shelly-energia/**

3. **Espera 1-2 minutos** (para dados começarem a chegar)

4. Faz **refresh** (F5 ou Ctrl+R)

5. **DEVE APARECER**:
   - ⚡ Potência TOTAL: Número (ex: 245W)
   - 🔴 Fase A: Número
   - 🟡 Fase B: Número
   - 🔵 Fase C: Número
   - 🔥 Pico Máximo Hoje
   - 📊 Gráficos a atualizar

✅ **TUDO A FUNCIONAR!**

---

## 🎉 PARABÉNS!

Tens agora:
- ✅ Collector a correr no Railway 24/7
- ✅ Dados do Shelly via Cloud (sem iMac)
- ✅ PostgreSQL com dados em tempo real
- ✅ Grafana a mostrar tudo

**ZERO dependências do iMac!**

---

## 💡 DICAS

### Ver logs em tempo real

1. Deployments → Deployment ativo → View Logs
2. Scroll até ao fundo
3. Vês dados a chegar a cada 60s

### Parar o collector (se necessário)

1. Settings → Service
2. Scroll até ao fundo
3. "Pause Service" ou "Delete Service"

### Mudar intervalo de coleta

1. Variables → COLLECTION_INTERVAL
2. Muda valor (ex: 30 para 30s, 300 para 5min)
3. Serviço reinicia automaticamente

---

## 📊 RESUMO DAS 5 VARIÁVEIS

Para teres à mão:

```
DATABASE_URL = ${{Postgres.DATABASE_URL}}  (referência)
SHELLY_CLOUD_SERVER = shelly-174-eu.shelly.cloud
SHELLY_AUTH_KEY = MmZjYzUydWlk115BA0F7C6074DEB3670AF7C65E406739E70D8FC9B71463C1C077EF4AECF12FCBB490A77E632D443
SHELLY_DEVICE_ID = 3030f9ec66ac
COLLECTION_INTERVAL = 60
```

---

## 🆘 AJUDA

Se ficares preso em algum passo:
1. Tira screenshot
2. Verifica se estás no projeto certo ("Password + PaginasVarias")
3. Confirma que o repositório GitHub é visível
4. Tenta fazer logout/login no Railway

---

**BOA SORTE! 🚀**

Demora **5 minutos** e fica tudo a funcionar perfeitamente!
