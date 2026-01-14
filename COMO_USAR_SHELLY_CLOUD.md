# 🌐 Como Usar Shelly Cloud API (SEM Tailscale!)

**Vantagem**: NÃO precisa de Tailscale, proxy, ou acesso à rede local!

---

## ✅ PRÉ-REQUISITOS

1. Shelly Pro 3EM conectado ao **Shelly Cloud**
2. App **Shelly Smart Control** instalada
3. Conta no Shelly Cloud

---

## 🔑 PASSO 1: Obter Credenciais do Shelly Cloud

### 1.1 Verificar se está no Cloud

1. Abre a app **Shelly Smart Control**
2. Verifica se o Shelly Pro 3EM aparece
3. Se aparece → Está conectado ao cloud ✅

### 1.2 Obter Auth Key

**Método A: Via App (Mais fácil)**

1. Abre **Shelly Smart Control**
2. Vai a **Settings** → **Cloud**
3. Procura **Server** - anota (ex: `shelly-13-eu.shelly.cloud`)
4. Procura **Auth Key** ou **API Key**

**Método B: Via Web**

1. Vai a https://control.shelly.cloud/
2. Faz login
3. Seleciona o Shelly Pro 3EM
4. Vai a **Settings** → **Developer Settings**
5. Copia o **Auth Key**

### 1.3 Obter Device ID

1. No Shelly Smart Control, abre o dispositivo
2. Vai a **Settings** → **Device Info**
3. Copia o **Device ID** (ex: `shellyem3-C45BBE123456`)

OU

1. Vai a https://control.shelly.cloud/
2. Clica no dispositivo
3. O ID aparece no URL: `https://control.shelly.cloud/device/{DEVICE_ID}`

---

## 🚀 PASSO 2: Configurar Collector no Railway

### 2.1 Atualizar Procfile

Edita o ficheiro `Procfile`:

```
worker: python collect_shelly_cloud.py
```

(Muda de `collect_shelly_postgres.py` para `collect_shelly_cloud.py`)

### 2.2 Deploy no Railway

1. Faz commit da mudança:
```bash
cd /root/shelly-collector-railway
git add Procfile collect_shelly_cloud.py COMO_USAR_SHELLY_CLOUD.md
git commit -m "Add: Shelly Cloud API collector (sem Tailscale)"
git push
```

2. Railway vai fazer redeploy automático

### 2.3 Configurar Variáveis

No Railway → Serviço `shelly-collector` → **Variables**:

```bash
DATABASE_URL
```
**Valor**: Referência ao PostgreSQL (já deve estar configurado)

```bash
SHELLY_CLOUD_SERVER
```
**Valor**: `shelly-13-eu.shelly.cloud` (ou o que anotaste na app)

Servidores possíveis:
- Europa: `shelly-13-eu.shelly.cloud`
- América do Norte: `shelly-13-us.shelly.cloud`
- Ásia: `shelly-13-asia.shelly.cloud`

```bash
SHELLY_AUTH_KEY
```
**Valor**: A auth key que copiaste (ex: `MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=`)

```bash
SHELLY_DEVICE_ID
```
**Valor**: O Device ID (ex: `shellyem3-C45BBE123456`)

```bash
COLLECTION_INTERVAL
```
**Valor**: `60` (opcional)

---

## ✅ PASSO 3: Verificar

### 3.1 Ver Logs no Railway

Railway → `shelly-collector` → **Deployments** → **View Logs**

Deve aparecer:
```
🌐 Shelly Pro 3EM → PostgreSQL Collector (Cloud API)
Shelly Cloud: shelly-13-eu.shelly.cloud
Device ID: shellyem3-C45BBE123456
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly Cloud
✓ Guardados 4 readings (Total: 245.32W)
Próxima coleta em 60s...
```

### 3.2 Verificar PostgreSQL

```sql
SELECT * FROM shelly_power_readings
WHERE timestamp > NOW() - INTERVAL '5 minutes'
ORDER BY timestamp DESC;
```

Deve ter dados NOVOS!

### 3.3 Ver no Grafana

https://grafana-production-db87.up.railway.app/d/shelly-energia/

Dados atualizam a cada 30-60s!

---

## 🆚 COMPARAÇÃO: Cloud API vs Local API

| Feature | Cloud API | Local API (Tailscale) |
|---------|-----------|----------------------|
| **Setup** | Fácil | Complexo |
| **Dependências** | Zero | Tailscale |
| **Latência** | ~500ms | ~50ms |
| **Dados disponíveis** | Todos | Todos |
| **Custo** | Grátis | Grátis |
| **Funciona se iMac estiver OFF** | ✅ SIM | ❌ NÃO |

**Recomendação**: USA CLOUD API! Muito mais simples! 🎉

---

## 🔧 TROUBLESHOOTING

### Erro: "Auth Key inválida"

- Verifica se copiaste a key completa
- Gera nova key no Shelly Cloud
- Certifica-te que não tem espaços extras

### Erro: "Device ID não encontrado"

- Verifica o ID no Shelly Smart Control
- Usa o formato completo: `shellyem3-XXXXXX`
- Confirma que o dispositivo está online no cloud

### Erro: "Sem dados do Shelly Cloud"

- Verifica se o dispositivo está **online** na app
- Testa a conexão internet do Shelly
- Verifica se escolheste o servidor correto (EU/US/Asia)

### Dados diferentes do esperado

A estrutura do JSON pode variar. Se o collector não funcionar, vou precisar ver um exemplo da resposta do cloud.

Podes testar manualmente:

```bash
curl -X POST https://shelly-13-eu.shelly.cloud/device/status \
  -H "Authorization: Bearer TUA_AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "TEU_DEVICE_ID",
    "auth_key": "TUA_AUTH_KEY"
  }'
```

Envia-me o JSON e adapto o código!

---

## 💰 CUSTO

- **Shelly Cloud**: Grátis
- **Railway**: ~€2/mês (Worker + PostgreSQL)
- **Total**: ~€2/mês

---

## 🎯 RESUMO

1. ✅ Obter Auth Key e Device ID do Shelly Cloud
2. ✅ Atualizar `Procfile` para usar `collect_shelly_cloud.py`
3. ✅ Git push (Railway redeploy automático)
4. ✅ Configurar variáveis no Railway
5. ✅ Verificar logs e Grafana

**MUITO MAIS SIMPLES QUE TAILSCALE!** 🚀

---

**Tens acesso ao Shelly Cloud?** Verifica na app e diz-me! Se sim, vamos por este caminho! 😊
