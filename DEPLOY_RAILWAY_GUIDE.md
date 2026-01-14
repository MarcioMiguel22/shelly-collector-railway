# 🚀 Guia de Deploy - Shelly Collector no Railway

**Código já está no GitHub**: https://github.com/MarcioMiguel22/shelly-collector-railway

---

## 📋 PASSOS PARA DEPLOY

### 1. Criar Novo Serviço no Railway

1. Vai a **https://railway.app/**
2. Abre o projeto do **Grafana** (onde já tens PostgreSQL e Grafana)
3. Clica em **+ New** → **GitHub Repo**
4. Seleciona **MarcioMiguel22/shelly-collector-railway**
5. Railway vai detectar automaticamente:
   - `Procfile` → Worker service
   - `runtime.txt` → Python 3.11.7
   - `requirements.txt` → Dependências

---

### 2. Configurar Variáveis de Ambiente

Depois do deploy, vai a **Variables** e adiciona:

```bash
# IP do Shelly (IMPORTANTE: Railway precisa aceder a este IP!)
SHELLY_IP=192.168.0.245

# PostgreSQL Railway (já existe no projeto, mas podes copiar manualmente)
DATABASE_URL=postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require

# Intervalo de coleta em segundos (opcional, default 60s)
COLLECTION_INTERVAL=60
```

**⚠️ IMPORTANTE - Variável `DATABASE_URL`**:
- Se estás no MESMO projeto Railway onde está o PostgreSQL, podes usar a variável automática
- Railway oferece `${{Postgres.DATABASE_URL}}` - usa isto em vez de copiar manualmente!

---

### 3. ⚠️ PROBLEMA: Acesso ao Shelly (192.168.0.245)

O Shelly está na tua **rede local** (192.168.0.245). O Railway está na **cloud**.

**3 Opções para resolver**:

#### **Opção A: Tailscale (RECOMENDADO para produção)**

1. Adiciona **Tailscale** ao Railway:
   - No projeto, clica **+ New** → **Template**
   - Procura "Tailscale"
   - Deploy do template Tailscale

2. Configura Tailscale:
   - Obtém auth key em https://login.tailscale.com/admin/settings/keys
   - Adiciona variável `TAILSCALE_AUTHKEY` no serviço Tailscale

3. Conecta tua rede ao Tailscale:
   - Instala Tailscale no teu router ou num dispositivo sempre ligado
   - O Shelly fica acessível via IP Tailscale

4. Atualiza `SHELLY_IP`:
   - Usa o IP Tailscale do dispositivo onde o Shelly está ligado
   - Exemplo: `SHELLY_IP=100.x.x.x`

#### **Opção B: Cloudflare Tunnel**

1. Cria Cloudflare Tunnel para tua rede:
   ```bash
   cloudflared tunnel create shelly-home
   ```

2. Configura tunnel para expor Shelly:
   ```yaml
   ingress:
     - hostname: shelly.teudominio.com
       service: http://192.168.0.245
   ```

3. Atualiza `SHELLY_IP`:
   ```bash
   SHELLY_IP=shelly.teudominio.com
   ```

#### **Opção C: Manter Collector Local (Temporário)**

Se preferires manter coleta local no iMac enquanto configuras acesso remoto:

```bash
# No iMac
cd /root/shelly-collector-railway
export SHELLY_IP="192.168.0.245"
export DATABASE_URL="postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require"
python3 collect_shelly_postgres.py
```

Dados vão diretamente para PostgreSQL Railway, mas coleta ainda depende do iMac.

---

### 4. Verificar Deploy

Depois de configurar variáveis:

1. **Ver Logs**:
   - No Railway → Serviço `shelly-collector` → **Deployments** → Último deploy → **View Logs**

2. **Output esperado**:
   ```
   ======================================================================
   🔌 Shelly Pro 3EM → PostgreSQL Collector
   ======================================================================
   Shelly IP: 192.168.0.245
   PostgreSQL: tramway.proxy.rlwy.net:46128/railway
   Intervalo de coleta: 60s
   Pressiona Ctrl+C para parar
   ======================================================================
   ✓ Conectado ao PostgreSQL Railway
   ✓ Tabelas verificadas/criadas

   --- Coleta #1 ---
   ✓ Dados recebidos do Shelly (192.168.0.245)
   ✓ Guardados 4 readings + 3 phase data (Total: 245.32W)
   Próxima coleta em 60s...
   ```

3. **Se der erro de conexão ao Shelly**:
   ```
   Erro ao buscar dados do Shelly: HTTPConnectionPool...
   ```
   → Precisas implementar uma das 3 opções acima!

---

### 5. Testar Dados no Grafana

1. Abre **Grafana**: https://grafana-production-db87.up.railway.app/d/shelly-3em-completo/
2. Verifica se os **novos dados** aparecem com:
   - ✅ Potência (W)
   - ✅ Corrente (A)
   - ✅ Tensão (V)
   - ✅ Fator de Potência
   - ✅ Frequência (Hz)

Se os dados antigos só tinham **power_w**, os novos terão **TODOS** os campos preenchidos!

---

## 🔧 TROUBLESHOOTING

### Problema: "Unable to connect to Shelly"

**Causa**: Railway não consegue aceder a 192.168.0.245 (rede local)

**Solução**: Implementa uma das 3 opções acima (Tailscale, Cloudflare Tunnel, ou manter local)

---

### Problema: "Error connecting to PostgreSQL"

**Verifica**:
1. `DATABASE_URL` tem `?sslmode=require` no final
2. Password está correta
3. PostgreSQL Railway está ativo

**Testar conexão**:
```bash
psql "postgresql://postgres:RFVUeMxciMxzOFmwucLcDYqovaPEBEDb@tramway.proxy.rlwy.net:46128/railway?sslmode=require" -c "SELECT 1"
```

---

### Problema: Deploy falha com "No release phase detected"

**Causa**: Railway não reconheceu o `Procfile`

**Solução**:
1. Vai a **Settings** → **Deploy**
2. Muda **Start Command** para:
   ```
   python collect_shelly_postgres.py
   ```

---

## 📊 VERIFICAR DADOS

Depois de alguns minutos (1-2 coletas), verifica na base de dados:

```sql
-- Ver últimas leituras
SELECT * FROM shelly_power_readings
ORDER BY timestamp DESC
LIMIT 10;

-- Ver se tem dados completos (corrente, tensão, etc.)
SELECT
    COUNT(*) as total,
    COUNT(current_a) as com_corrente,
    COUNT(voltage_v) as com_tensao,
    COUNT(power_factor) as com_fator_potencia
FROM shelly_power_readings
WHERE timestamp > NOW() - INTERVAL '10 minutes';
```

Se `com_corrente`, `com_tensao`, `com_fator_potencia` forem > 0, está tudo a funcionar! 🎉

---

## 🎯 PRÓXIMO PASSO

Depois de confirmar que está tudo a funcionar:

1. ✅ Apagar serviços antigos no Railway (`shelly-sync-railway` se existir)
2. ✅ Desativar InfluxDB Cloud (já não é necessário)
3. ✅ Parar Grafana local no iMac (se estiveres a usar Railway apenas)

---

**Última Atualização**: 2026-01-14
**Criado por**: Márcio Miguel + Claude
