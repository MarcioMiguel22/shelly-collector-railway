# ✅ CHECKLIST FINAL - Setup Completo Shelly Pro 3EM

**Data de criação**: 2026-01-14
**Arquitetura**: PostgreSQL Only (sem InfluxDB, sem iMac)

---

## 📦 REPOSITÓRIO GITHUB

- [x] ✅ Código no GitHub: https://github.com/MarcioMiguel22/shelly-collector-railway
- [x] ✅ README.md completo com badges e documentação
- [x] ✅ DEPLOY_RAILWAY_GUIDE.md (guia detalhado)
- [x] ✅ DEPLOY_AGORA.md (guia ultra-rápido 3 passos)
- [x] ✅ CEREBRO_SISTEMA_SHELLY_RAILWAY.md (documentação técnica)
- [x] ✅ Todos os ficheiros necessários (Procfile, requirements.txt, runtime.txt)

---

## 🗄️ POSTGRESQL RAILWAY

- [x] ✅ PostgreSQL criado: `tramway.proxy.rlwy.net:46128`
- [x] ✅ Tabelas criadas:
  - [x] `shelly_power_readings` (principal)
  - [x] `shelly_phase_data` (detalhado)
  - [x] `shelly_energy_summary` (acumulado)
  - [x] `shelly_device_info` (status)
- [x] ✅ Índices otimizados criados
- [x] ✅ Dados migrados do InfluxDB (48 registos de teste)
- [x] ✅ Conexão SSL configurada (`?sslmode=require`)

**Credenciais**:
```
Host: tramway.proxy.rlwy.net
Port: 46128
Database: railway
User: postgres
Password: RFVUeMxciMxzOFmwucLcDYqovaPEBEDb
```

---

## 📊 GRAFANA RAILWAY

- [x] ✅ Grafana deployado: https://grafana-production-db87.up.railway.app/
- [x] ✅ Acesso anónimo ativado (Admin role)
- [x] ✅ Datasource PostgreSQL criado: `postgres-shelly-backup-2025`
- [x] ✅ Datasource testado (Health: OK)
- [x] ✅ Dashboard completo criado: **⚡ Shelly Pro 3EM - Monitor Completo**
  - [x] 4 stats principais (Potência, Corrente, Tensão, Frequência)
  - [x] Gráfico de potência total
  - [x] Gráficos por fase (A/B/C) com cores (🔴/🟡/🔵)
  - [x] Fator de potência
  - [x] Tabela com últimas 50 leituras
- [x] ✅ Dashboards antigos apagados (3 dashboards removidos)
- [x] ✅ Auto-refresh configurado (30s)

**Dashboard URL**: https://grafana-production-db87.up.railway.app/d/shelly-3em-completo/

---

## 🔌 COLLECTOR (SHELLY → POSTGRESQL)

### Código Pronto
- [x] ✅ `collect_shelly_postgres.py` criado
- [x] ✅ Suporte completo para todas as métricas:
  - [x] Potência (W) - Total + por fase
  - [x] Corrente (A) - Total + por fase
  - [x] Tensão (V) - Total + por fase
  - [x] Fator de Potência - Por fase
  - [x] Frequência (Hz) - Rede
  - [x] Potência reativa/aparente
  - [x] Energia acumulada
- [x] ✅ Configurável via variáveis de ambiente
- [x] ✅ Logging completo
- [x] ✅ Retry logic e error handling

### Deploy Railway
- [ ] ⏳ **PENDENTE**: Criar serviço no Railway
- [ ] ⏳ **PENDENTE**: Configurar variáveis:
  - [ ] `DATABASE_URL` (referência ao PostgreSQL)
  - [ ] `SHELLY_IP` (192.168.0.245 ou Tailscale IP)
  - [ ] `COLLECTION_INTERVAL` (60)
- [ ] ⏳ **PENDENTE**: Resolver acesso ao Shelly:
  - [ ] Opção 1: Tailscale
  - [ ] Opção 2: Cloudflare Tunnel
  - [ ] Opção 3: Executar localmente (temporário)
- [ ] ⏳ **PENDENTE**: Verificar logs
- [ ] ⏳ **PENDENTE**: Confirmar dados a chegar no PostgreSQL

**Guias disponíveis**:
- 📖 [DEPLOY_AGORA.md](DEPLOY_AGORA.md) - 3 passos rápidos
- 📖 [DEPLOY_RAILWAY_GUIDE.md](DEPLOY_RAILWAY_GUIDE.md) - Guia completo

---

## 🧹 LIMPEZA DE SERVIÇOS

### Railway
- [ ] ⏳ **PENDENTE**: Apagar `shelly-sync-railway` (se existir)
- [ ] ⏳ **PENDENTE**: Apagar PostgreSQL antigo `switchback` (se for serviço separado)
- [ ] ⏳ **PENDENTE**: Apagar quaisquer serviços relacionados com InfluxDB

**Como verificar**:
1. Abre https://railway.app/
2. Seleciona projeto Grafana
3. Vê lista de serviços
4. Apaga os obsoletos (clica serviço → Settings → Delete Service)

### InfluxDB Cloud
- [ ] ⏳ **PENDENTE**: Desativar/apagar bucket `energy` (DEPOIS de confirmar dados no PostgreSQL)
- [ ] ⏳ **PENDENTE**: Cancelar subscrição InfluxDB (se aplicável)

### iMac/Servidor Local
- [ ] ⏳ **PENDENTE**: Parar Grafana local (se aplicável)
- [ ] ⏳ **PENDENTE**: Parar collector local (se aplicável)
- [ ] ⏳ **PENDENTE**: Remover cronjobs relacionados (se aplicável)

---

## 🧪 TESTES E VERIFICAÇÃO

### Testes de Dados
- [ ] ⏳ **PENDENTE**: Verificar dados completos no PostgreSQL:
  ```sql
  SELECT
      COUNT(*) as total,
      COUNT(current_a) as com_corrente,
      COUNT(voltage_v) as com_tensao,
      COUNT(power_factor) as com_fator_potencia
  FROM shelly_power_readings
  WHERE timestamp > NOW() - INTERVAL '10 minutes';
  ```
  **Esperado**: `com_corrente`, `com_tensao`, `com_fator_potencia` > 0

### Testes de Grafana
- [ ] ⏳ **PENDENTE**: Abrir dashboard e verificar TODOS os painéis:
  - [ ] Potência TOTAL Atual (deve mostrar valor em W)
  - [ ] Corrente TOTAL Atual (deve mostrar valor em A)
  - [ ] Tensão Média (deve mostrar ~230V)
  - [ ] Frequência (deve mostrar ~50Hz)
  - [ ] Gráfico de potência total
  - [ ] Gráficos por fase (A/B/C)
  - [ ] Fator de potência
  - [ ] Tabela com dados

### Testes de Estabilidade
- [ ] ⏳ **PENDENTE**: Deixar collector a correr durante 24h
- [ ] ⏳ **PENDENTE**: Verificar se não há erros nos logs
- [ ] ⏳ **PENDENTE**: Confirmar que dados continuam a chegar

---

## 📖 DOCUMENTAÇÃO

- [x] ✅ README.md com instruções completas
- [x] ✅ DEPLOY_AGORA.md (guia rápido)
- [x] ✅ DEPLOY_RAILWAY_GUIDE.md (guia detalhado)
- [x] ✅ CEREBRO_SISTEMA_SHELLY_RAILWAY.md (documentação técnica)
- [x] ✅ CHECKLIST_FINAL.md (este ficheiro)
- [x] ✅ Credenciais documentadas
- [x] ✅ Queries SQL de exemplo
- [x] ✅ Troubleshooting guide

---

## 💰 CUSTOS

**Antes** (com InfluxDB):
- InfluxDB Cloud: €0-10/mês (dependendo do uso)
- iMac sempre ligado: Custo elétrico

**Depois** (PostgreSQL Only):
- Railway Worker: ~€1/mês
- PostgreSQL Railway: ~€1/mês (ou grátis no free tier)
- **Total: ~€0-2/mês** 🎉

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

1. **Deploy do Collector** (PRIORIDADE 1)
   - Segue [DEPLOY_AGORA.md](DEPLOY_AGORA.md)
   - Resolve acesso ao Shelly (Tailscale recomendado)

2. **Verificar Dados** (PRIORIDADE 2)
   - Confirma que dados completos chegam ao PostgreSQL
   - Verifica dashboard no Grafana

3. **Limpar Serviços** (PRIORIDADE 3)
   - Apaga serviços obsoletos no Railway
   - Desativa InfluxDB Cloud

---

## ✅ CRITÉRIOS DE SUCESSO

O setup está **100% funcional** quando:

- ✅ Collector a correr 24/7 no Railway (ou localmente)
- ✅ Dados a chegar ao PostgreSQL a cada 60s
- ✅ TODOS os campos preenchidos: `power_w`, `current_a`, `voltage_v`, `power_factor`, `frequency_hz`
- ✅ Dashboard Grafana a mostrar dados em tempo real
- ✅ Sem erros nos logs durante 24h
- ✅ Zero dependências do iMac/InfluxDB

---

## 📞 SUPORTE

**Documentação**:
- 📖 README.md - Visão geral
- 📖 DEPLOY_AGORA.md - Deploy rápido
- 📖 DEPLOY_RAILWAY_GUIDE.md - Deploy detalhado
- 📖 CEREBRO_SISTEMA_SHELLY_RAILWAY.md - Referência técnica

**Repositório**: https://github.com/MarcioMiguel22/shelly-collector-railway

**Dashboard Grafana**: https://grafana-production-db87.up.railway.app/d/shelly-3em-completo/

---

**Última Atualização**: 2026-01-14
**Status**: 🟡 Parcialmente completo - Falta deploy do collector
**Criado por**: Márcio Miguel + Claude
