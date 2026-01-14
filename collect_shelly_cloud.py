#!/usr/bin/env python3
"""
Shelly Pro 3EM → PostgreSQL Collector (via Shelly Cloud API)
Coleta dados via API Cloud do Shelly - NÃO precisa de Tailscale!
"""

import os
import sys
import time
import logging
import requests
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_batch

# Configuração Shelly Cloud
SHELLY_CLOUD_SERVER = os.getenv('SHELLY_CLOUD_SERVER', 'shelly-13-eu.shelly.cloud')
SHELLY_AUTH_KEY = os.getenv('SHELLY_AUTH_KEY', '')  # Key do Shelly Cloud
SHELLY_DEVICE_ID = os.getenv('SHELLY_DEVICE_ID', '')  # ID do dispositivo

# Configuração PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', '')
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '60'))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShellyCloudCollector:
    def __init__(self):
        self.pg_conn = None
        self.device_id = 'shelly_3em_entrada'
        self.cloud_url = f"https://{SHELLY_CLOUD_SERVER}/device/status"

    def connect_postgres(self):
        """Conecta ao PostgreSQL Railway"""
        try:
            self.pg_conn = psycopg2.connect(DATABASE_URL)
            logger.info("✓ Conectado ao PostgreSQL Railway")
            self.create_tables()
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
            return False

    def create_tables(self):
        """Cria tabelas se não existirem"""
        try:
            cursor = self.pg_conn.cursor()

            # Tabela principal
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shelly_power_readings (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    device_id VARCHAR(100) NOT NULL,
                    phase VARCHAR(10) NOT NULL,
                    power_w REAL,
                    current_a REAL,
                    voltage_v REAL,
                    power_factor REAL,
                    frequency_hz REAL,
                    UNIQUE (timestamp, device_id, phase)
                )
            """)

            # Índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_power_readings_timestamp
                ON shelly_power_readings(timestamp DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_power_readings_phase
                ON shelly_power_readings(phase, timestamp DESC)
            """)

            self.pg_conn.commit()
            cursor.close()
            logger.info("✓ Tabelas verificadas/criadas")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            self.pg_conn.rollback()

    def fetch_shelly_cloud_data(self):
        """Busca dados via Shelly Cloud API"""
        try:
            headers = {
                "Authorization": f"Bearer {SHELLY_AUTH_KEY}"
            }

            params = {
                "id": SHELLY_DEVICE_ID,
                "auth_key": SHELLY_AUTH_KEY
            }

            response = requests.post(
                self.cloud_url,
                headers=headers,
                json=params,
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            logger.info(f"✓ Dados recebidos do Shelly Cloud")
            return data.get('data', {}).get('device_status', {})

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar dados do Shelly Cloud: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao processar dados do Shelly Cloud: {e}")
            return None

    def parse_and_save(self, data):
        """Processa e guarda dados no PostgreSQL"""
        if not data:
            return

        timestamp = datetime.now()

        try:
            cursor = self.pg_conn.cursor()

            # Extrair dados das 3 fases do response do cloud
            phases = ['a', 'b', 'c']
            total_power = 0
            total_current = 0
            total_voltage = 0

            readings = []

            # Cloud API retorna estrutura diferente - adaptar conforme resposta real
            emeters = data.get('emeters', [])

            if not emeters or len(emeters) < 3:
                logger.warning("⚠️ Dados incompletos do cloud")
                return

            for idx, phase_letter in enumerate(phases):
                phase_upper = phase_letter.upper()
                emeter = emeters[idx] if idx < len(emeters) else {}

                power = emeter.get('power', 0)
                current = emeter.get('current', 0)
                voltage = emeter.get('voltage', 0)
                pf = emeter.get('pf', 0)
                freq = 50.0  # Cloud pode não fornecer - assumir 50Hz

                total_power += power
                total_current += current
                total_voltage += voltage

                readings.append((
                    timestamp,
                    self.device_id,
                    phase_upper,
                    power,
                    current,
                    voltage,
                    pf,
                    freq
                ))

            # Reading total
            avg_voltage = total_voltage / 3 if total_voltage > 0 else 0

            readings.append((
                timestamp,
                self.device_id,
                'total',
                total_power,
                total_current,
                avg_voltage,
                None,
                50.0
            ))

            # Inserir
            insert_query = """
                INSERT INTO shelly_power_readings
                (timestamp, device_id, phase, power_w, current_a, voltage_v, power_factor, frequency_hz)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, device_id, phase) DO UPDATE SET
                    power_w = EXCLUDED.power_w,
                    current_a = EXCLUDED.current_a,
                    voltage_v = EXCLUDED.voltage_v,
                    power_factor = EXCLUDED.power_factor,
                    frequency_hz = EXCLUDED.frequency_hz
            """
            execute_batch(cursor, insert_query, readings, page_size=10)
            self.pg_conn.commit()
            cursor.close()

            logger.info(f"✓ Guardados {len(readings)} readings (Total: {total_power:.2f}W)")

        except Exception as e:
            logger.error(f"Erro ao guardar dados: {e}")
            self.pg_conn.rollback()

    def run(self):
        """Loop principal de coleta"""
        logger.info("=" * 70)
        logger.info("🌐 Shelly Pro 3EM → PostgreSQL Collector (Cloud API)")
        logger.info("=" * 70)
        logger.info(f"Shelly Cloud: {SHELLY_CLOUD_SERVER}")
        logger.info(f"Device ID: {SHELLY_DEVICE_ID}")
        logger.info(f"Intervalo de coleta: {COLLECTION_INTERVAL}s")
        logger.info("Pressiona Ctrl+C para parar")
        logger.info("=" * 70)

        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL não configurado!")
            sys.exit(1)

        if not SHELLY_AUTH_KEY:
            logger.error("❌ SHELLY_AUTH_KEY não configurado!")
            sys.exit(1)

        if not SHELLY_DEVICE_ID:
            logger.error("❌ SHELLY_DEVICE_ID não configurado!")
            sys.exit(1)

        if not self.connect_postgres():
            logger.error("❌ Falha ao conectar ao PostgreSQL")
            sys.exit(1)

        collection_count = 0

        try:
            while True:
                collection_count += 1
                logger.info(f"\n--- Coleta #{collection_count} ---")

                data = self.fetch_shelly_cloud_data()
                if data:
                    self.parse_and_save(data)
                else:
                    logger.warning("⚠️ Sem dados do Shelly Cloud nesta iteração")

                logger.info(f"Próxima coleta em {COLLECTION_INTERVAL}s...")
                time.sleep(COLLECTION_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\n⏹ Parando collector...")
        except Exception as e:
            logger.error(f"Erro fatal: {e}")
        finally:
            if self.pg_conn:
                self.pg_conn.close()
                logger.info("✓ Conexão fechada")

def main():
    collector = ShellyCloudCollector()
    collector.run()

if __name__ == "__main__":
    main()
