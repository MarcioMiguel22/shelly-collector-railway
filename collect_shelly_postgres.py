#!/usr/bin/env python3
"""
Shelly Pro 3EM → PostgreSQL Collector
Coleta dados direto do Shelly e guarda no PostgreSQL Railway
Sem dependência do iMac ou InfluxDB
"""

import os
import sys
import time
import logging
import requests
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_batch

# Configuração
SHELLY_IP = os.getenv('SHELLY_IP', '192.168.0.245')
SHELLY_URL = f"http://{SHELLY_IP}/rpc/EM.GetStatus?id=0"
DATABASE_URL = os.getenv('DATABASE_URL', '')
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '60'))  # 1 minuto

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ShellyCollector:
    def __init__(self):
        self.pg_conn = None
        self.device_id = 'shelly_3em_entrada'

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

            # Tabela principal de leituras
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

            # Tabela de dados por fase
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shelly_phase_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    device_id VARCHAR(100) NOT NULL,
                    phase VARCHAR(10) NOT NULL,
                    power_w REAL,
                    reactive_power_var REAL,
                    apparent_power_va REAL,
                    current_a REAL,
                    voltage_v REAL,
                    power_factor REAL,
                    frequency_hz REAL
                )
            """)

            # Tabela de energia acumulada
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shelly_energy_summary (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    device_id VARCHAR(100) NOT NULL,
                    total_active_energy_wh REAL,
                    total_reactive_energy_varh REAL,
                    total_returned_energy_wh REAL,
                    max_power_w REAL,
                    min_power_w REAL,
                    avg_power_w REAL
                )
            """)

            # Tabela de informação do dispositivo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shelly_device_info (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    device_id VARCHAR(100) NOT NULL,
                    firmware_version VARCHAR(50),
                    uptime_seconds INTEGER,
                    temperature_c REAL,
                    wifi_rssi INTEGER
                )
            """)

            # Índices para performance
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

    def fetch_shelly_data(self):
        """Busca dados do Shelly Pro 3EM"""
        try:
            response = requests.get(SHELLY_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✓ Dados recebidos do Shelly ({SHELLY_IP})")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar dados do Shelly: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao processar dados do Shelly: {e}")
            return None

    def parse_and_save(self, data):
        """Processa e guarda dados no PostgreSQL"""
        if not data:
            return

        timestamp = datetime.now()

        try:
            cursor = self.pg_conn.cursor()

            # Extrair dados das 3 fases
            phases = ['a', 'b', 'c']
            total_power = 0
            total_current = 0
            total_voltage = 0

            readings = []
            phase_data = []

            for idx, phase in enumerate(phases):
                phase_key = f"phase_{phase}"
                phase_upper = phase.upper()

                if phase_key in data:
                    phase_info = data[phase_key]

                    power = phase_info.get('act_power', 0)
                    current = phase_info.get('current', 0)
                    voltage = phase_info.get('voltage', 0)
                    pf = phase_info.get('pf', 0)
                    freq = phase_info.get('freq', 0)

                    total_power += power
                    total_current += current
                    total_voltage += voltage

                    # Reading para cada fase
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

                    # Dados detalhados por fase
                    phase_data.append((
                        timestamp,
                        self.device_id,
                        phase_upper,
                        power,
                        phase_info.get('react_power', 0),
                        phase_info.get('aprt_power', 0),
                        current,
                        voltage,
                        pf,
                        freq
                    ))

            # Reading total (soma das 3 fases)
            avg_voltage = total_voltage / 3 if total_voltage > 0 else 0
            avg_freq = data.get('phase_a', {}).get('freq', 50)

            readings.append((
                timestamp,
                self.device_id,
                'total',
                total_power,
                total_current,
                avg_voltage,
                None,  # power_factor (não aplicável para total)
                avg_freq
            ))

            # Inserir readings
            insert_readings = """
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
            execute_batch(cursor, insert_readings, readings)

            # Inserir phase data
            insert_phase = """
                INSERT INTO shelly_phase_data
                (timestamp, device_id, phase, power_w, reactive_power_var, apparent_power_va,
                 current_a, voltage_v, power_factor, frequency_hz)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_batch(cursor, insert_phase, phase_data)

            # Inserir energy summary se disponível
            if 'total_act_energy' in data:
                cursor.execute("""
                    INSERT INTO shelly_energy_summary
                    (timestamp, device_id, total_active_energy_wh, total_reactive_energy_varh,
                     total_returned_energy_wh, max_power_w, min_power_w, avg_power_w)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    timestamp,
                    self.device_id,
                    data.get('total_act_energy', 0),
                    data.get('total_react_energy', 0),
                    data.get('total_act_ret_energy', 0),
                    total_power,  # max neste momento
                    total_power,  # min neste momento
                    total_power   # avg neste momento
                ))

            self.pg_conn.commit()
            cursor.close()

            logger.info(f"✓ Guardados {len(readings)} readings + {len(phase_data)} phase data (Total: {total_power:.2f}W)")

        except Exception as e:
            logger.error(f"Erro ao guardar dados: {e}")
            self.pg_conn.rollback()

    def run(self):
        """Loop principal de coleta"""
        logger.info("=" * 70)
        logger.info("🔌 Shelly Pro 3EM → PostgreSQL Collector")
        logger.info("=" * 70)
        logger.info(f"Shelly IP: {SHELLY_IP}")
        logger.info(f"PostgreSQL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Railway'}")
        logger.info(f"Intervalo de coleta: {COLLECTION_INTERVAL}s")
        logger.info("Pressiona Ctrl+C para parar")
        logger.info("=" * 70)

        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL não configurado!")
            sys.exit(1)

        if not self.connect_postgres():
            logger.error("❌ Falha ao conectar ao PostgreSQL")
            sys.exit(1)

        collection_count = 0

        try:
            while True:
                collection_count += 1
                logger.info(f"\n--- Coleta #{collection_count} ---")

                data = self.fetch_shelly_data()
                if data:
                    self.parse_and_save(data)
                else:
                    logger.warning("⚠️ Sem dados do Shelly nesta iteração")

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
    collector = ShellyCollector()
    collector.run()

if __name__ == "__main__":
    main()
