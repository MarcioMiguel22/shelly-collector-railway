# 🔐 Setup Tailscale + Railway - Acesso ao Shelly

**Objetivo**: Railway conseguir aceder ao Shelly (192.168.0.245) na tua rede local.

---

## 📋 O QUE PRECISAS

1. Conta Tailscale (grátis) - https://login.tailscale.com/
2. Tailscale instalado no iMac (ou router)
3. Tailscale no Railway
4. 15 minutos

---

## 🚀 PASSO 1: Criar Conta Tailscale

1. Vai a **https://login.tailscale.com/start**
2. Faz login com GitHub/Google/Email
3. Aceita permissões

✅ Tens uma **Tailnet** (rede virtual privada)

---

## 🖥️ PASSO 2: Instalar Tailscale no iMac

### Opção A: Via Homebrew (Recomendado)

```bash
# Instalar
brew install tailscale

# Iniciar serviço
sudo tailscaled install-system-daemon
tailscale up
```

### Opção B: Download Manual

1. Vai a https://tailscale.com/download/mac
2. Descarrega e instala
3. Abre Tailscale e faz login

### Verificar

```bash
tailscale status
```

Deve aparecer:
```
100.x.x.x   imac-nome    marcio@  macOS   -
```

✅ iMac está na Tailnet!

---

## 🔑 PASSO 3: Gerar Auth Key para Railway

1. Vai a **https://login.tailscale.com/admin/settings/keys**
2. Clica **Generate auth key**
3. Configura:
   - ✅ **Reusable**: ON
   - ✅ **Ephemeral**: OFF
   - ✅ **Pre-approved**: ON
   - ⏱️ **Expiration**: 90 days (ou mais)
4. Clica **Generate key**
5. **COPIA** a key (começa com `tskey-auth-...`)

⚠️ **GUARDA ESTA KEY** - Vais precisar dela!

---

## ☁️ PASSO 4: Adicionar Tailscale ao Railway

### 4.1 Criar Serviço Tailscale

1. Vai a **https://railway.app/**
2. Abre o projeto do **Grafana**
3. Clica **+ New**
4. Seleciona **Empty Service**
5. Nome: `tailscale-gateway`

### 4.2 Configurar Dockerfile

No serviço `tailscale-gateway`:

1. Vai a **Settings** → **Source**
2. Seleciona **Dockerfile**
3. Clica **Add Dockerfile**

Cria ficheiro `Dockerfile`:

```dockerfile
FROM tailscale/tailscale:latest

# Executar Tailscale
CMD ["tailscaled", "--tun=userspace-networking", "--socks5-server=localhost:1055"]
```

### 4.3 Adicionar Variáveis

No serviço `tailscale-gateway` → **Variables**:

```bash
TAILSCALE_AUTH_KEY
```
**Valor**: Cola a auth key que copiaste (`tskey-auth-...`)

```bash
TAILSCALE_HOSTNAME
```
**Valor**: `railway-gateway`

### 4.4 Deploy

Clica **Deploy** - Railway vai criar o serviço Tailscale

---

## 📡 PASSO 5: Configurar Railway para Usar Tailscale

### 5.1 Ativar Subnet Routes (Opcional - Avançado)

Se quiseres que Railway aceda a TODA a tua rede local (192.168.0.0/24):

**No iMac**:
```bash
tailscale up --advertise-routes=192.168.0.0/24
```

**No Tailscale Admin** (https://login.tailscale.com/admin/machines):
1. Encontra o iMac
2. Clica nos **3 pontos** → **Edit route settings**
3. Ativa a rota `192.168.0.0/24`
4. **Save**

### 5.2 Verificar IPs Tailscale

**No iMac**:
```bash
tailscale status
```

Anota os IPs:
```
100.x.x.x   imac-nome           marcio@  macOS   -
100.y.y.y   railway-gateway     -        linux   -
```

---

## 🔌 PASSO 6: Atualizar Collector para Usar Tailscale

### Opção A: Usar Subnet Route (se configuraste)

No Railway → Serviço `shelly-collector` → **Variables**:

```bash
SHELLY_IP=192.168.0.245
```

(Continua a usar IP local - Tailscale faz routing)

### Opção B: Usar IP Tailscale do iMac

**Descobrir IP do Shelly via Tailscale**:

Como o Shelly não tem Tailscale, tens 2 opções:

**B1: Proxy via iMac** (Recomendado)

No iMac, cria um proxy simples:
```bash
# Instalar socat
brew install socat

# Criar proxy HTTP para o Shelly
socat TCP-LISTEN:8245,fork TCP:192.168.0.245:80
```

No Railway → `shelly-collector` → **Variables**:
```bash
SHELLY_IP=100.x.x.x:8245
```
(Usa o IP Tailscale do iMac + porta 8245)

**B2: Ativar IP Forwarding no iMac**

```bash
sudo sysctl -w net.inet.ip.forwarding=1
```

Depois usa subnet route (Opção A).

---

## 🚀 PASSO 7: Deploy do Collector

### 7.1 Criar Serviço no Railway

1. Vai ao projeto Grafana
2. Clica **+ New** → **GitHub Repo**
3. Seleciona **shelly-collector-railway**
4. Railway faz deploy automático

### 7.2 Configurar Variáveis

No serviço `shelly-collector` → **Variables**:

```bash
DATABASE_URL
```
**Valor**: Clica **Add Reference** → Seleciona **PostgreSQL** → `DATABASE_URL`

```bash
SHELLY_IP
```
**Valor**:
- Se usaste subnet route: `192.168.0.245`
- Se usaste proxy: `100.x.x.x:8245` (IP Tailscale do iMac)

```bash
COLLECTION_INTERVAL
```
**Valor**: `60`

### 7.3 Configurar Network (IMPORTANTE!)

Para o collector usar o Tailscale:

**Método 1: Shared Network** (Mais simples)

No Railway, os serviços no mesmo projeto podem partilhar rede via:

1. Vai a **Settings** do serviço `shelly-collector`
2. Procura **Networking** → **Private Networking**
3. Ativa **Private Networking**
4. Faz o mesmo no `tailscale-gateway`

⚠️ **PROBLEMA**: Railway não suporta nativamente partilha de interface Tailscale entre serviços.

**Método 2: Tailscale em CADA serviço** (Recomendado)

Modifica o `Dockerfile` do collector para incluir Tailscale:

```dockerfile
FROM python:3.11.7-slim

# Instalar Tailscale
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://tailscale.com/install.sh | sh

# Copiar código
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Script de startup
COPY <<'EOF' /start.sh
#!/bin/bash
# Iniciar Tailscale em background
tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &
sleep 2
tailscale up --authkey=${TAILSCALE_AUTH_KEY} --hostname=shelly-collector

# Aguardar conexão
while ! tailscale status --json | grep -q "Online"; do
  echo "Aguardando Tailscale..."
  sleep 2
done

# Executar collector
exec python collect_shelly_postgres.py
EOF

RUN chmod +x /start.sh
CMD ["/start.sh"]
```

Adiciona variável no collector:
```bash
TAILSCALE_AUTH_KEY=tskey-auth-...
```

---

## ✅ PASSO 8: Verificar

### 8.1 Ver Logs do Collector

No Railway → `shelly-collector` → **Deployments** → **View Logs**

Deve aparecer:
```
🔌 Shelly Pro 3EM → PostgreSQL Collector
Tailscale conectado!
✓ Conectado ao PostgreSQL Railway
✓ Tabelas verificadas/criadas

--- Coleta #1 ---
✓ Dados recebidos do Shelly (192.168.0.245)
✓ Guardados 4 readings + 3 phase data (Total: 245.32W)
```

### 8.2 Verificar PostgreSQL

```sql
SELECT * FROM shelly_power_readings
WHERE timestamp > NOW() - INTERVAL '5 minutes'
ORDER BY timestamp DESC;
```

Deve ter dados NOVOS com:
- ✅ `power_w`
- ✅ `current_a`
- ✅ `voltage_v`
- ✅ `power_factor`
- ✅ `frequency_hz`

### 8.3 Ver no Grafana

https://grafana-production-db87.up.railway.app/d/shelly-energia/

Dados devem atualizar a cada 30s!

---

## 🔧 TROUBLESHOOTING

### Erro: "Cannot connect to Shelly"

**Verificar**:
```bash
# No Railway logs do collector
# Deve aparecer IP Tailscale
```

**Testar no iMac**:
```bash
tailscale status
curl http://192.168.0.245/rpc/EM.GetStatus?id=0
```

### Erro: "Tailscale not authorized"

- Gera nova auth key
- Verifica se é **Reusable** e **Pre-approved**

### Collector não vê o Shelly via Tailscale

**Usar proxy no iMac**:
```bash
# Terminal no iMac
socat TCP-LISTEN:8245,fork TCP:192.168.0.245:80 &

# No Railway
SHELLY_IP=<IP_TAILSCALE_DO_IMAC>:8245
```

---

## 📝 RESUMO

1. ✅ Instalar Tailscale no iMac
2. ✅ Gerar auth key no Tailscale admin
3. ✅ Adicionar Tailscale ao collector no Railway (via Dockerfile)
4. ✅ Configurar variáveis (DATABASE_URL, SHELLY_IP, TAILSCALE_AUTH_KEY)
5. ✅ Deploy e verificar logs
6. ✅ Verificar dados no Grafana

---

## 💰 CUSTO

- **Tailscale**: Grátis (até 100 dispositivos)
- **Railway**: ~€2/mês (Worker + PostgreSQL)
- **Total**: ~€2/mês

---

**Pronto para começar?** 🚀

Começa pelo **PASSO 2** (instalar Tailscale no iMac) e depois vou ajudar-te com o resto!
