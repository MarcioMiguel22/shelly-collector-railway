#!/usr/bin/env python3
"""
Migração única: InfluxDB → PostgreSQL
Copia histórico de dados do InfluxDB Cloud para PostgreSQL Railway
"""

import os
import sys
from datetime import datetime
from influxdb_client import InfluxDBClient
import psycopg2
from psycopg2.extras import execute_batch
import logging

# Configuração InfluxDB
INFLUX_URL = os.getenv('INFLUX_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
INFLUX_ORG = os.getenv('INFLUX_ORG', 'MÁRCIOV ÁRIOSPRO')
INFLUX_TOKEN = os.getenv('INFLUX_TOKEN', 'rE69yYhRgXAzF0X7D37zkScPe_-ft1eWNUrmHTFFOoJc_lexGom5fFHsk-07eWxAztvBeOpcpN8Dpt7JyIdouw==')
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET', 'energy')

# Configuração PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:qiUTzNhdGXGkDtpTDOoGRBJoAvwBLUub@switchback.proxy.rlwy.net:47559/railway')

# Quantos dias de histórico migrar
MIGRATION_DAYS = int(os.getenv('MIGRATION_DAYS', '30'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate():
    """Migra dados do InfluxDB para PostgreSQL"""
    logger.info("=" * 70)
    logger.info("📦 Migração: InfluxDB → PostgreSQL")
    logger.info("=" * 70)
    logger.info(f"Período: Últimos {MIGRATION_DAYS} dias")
    logger.info("=" * 70)

    # Conectar InfluxDB
    logger.info("Conectando ao InfluxDB...")
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = influx_client.query_api()

    # Conectar PostgreSQL
    logger.info("Conectando ao PostgreSQL...")
    pg_conn = psycopg2.connect(DATABASE_URL)
    cursor = pg_conn.cursor()

    try:
        # Query para potência total
        logger.info(f"Buscando dados de potência total (últimos {MIGRATION_DAYS} dias)...")
        query_total = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -{MIGRATION_DAYS}d)
          |> filter(fn: (r) => r["_measurement"] == "power")
          |> filter(fn: (r) => r["_field"] == "phase_a" or r["_field"] == "phase_b" or r["_field"] == "phase_c")
          |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> map(fn: (r) => ({{ r with total: r.phase_a + r.phase_b + r.phase_c }}))
        '''

        result = query_api.query(query_total)

        data = []
        for table in result:
            for record in table.records:
                total_power = record.values.get("total", 0)
                if total_power > 0:
                    data.append((
                        record.get_time(),
                        'shelly_3em_entrada',
                        'total',
                        total_power,
                        None, None, None, None
                    ))

        logger.info(f"✓ Obtidos {len(data)} registos de potência total")

        # Inserir no PostgreSQL
        if data:
            insert_query = """
                INSERT INTO shelly_power_readings
                (timestamp, device_id, phase, power_w, current_a, voltage_v, power_factor, frequency_hz)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, device_id, phase) DO NOTHING
            """
            execute_batch(cursor, insert_query, data, page_size=500)
            pg_conn.commit()
            logger.info(f"✓ Migrados {len(data)} registos de potência total")

        # Query para dados por fase
        logger.info(f"Buscando dados por fase (últimos {MIGRATION_DAYS} dias)...")

        phases_data = []
        for phase_letter, phase_name in [('a', 'A'), ('b', 'B'), ('c', 'C')]:
            query_phase = f'''
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -{MIGRATION_DAYS}d)
              |> filter(fn: (r) => r["_measurement"] == "power")
              |> filter(fn: (r) => r["_field"] == "phase_{phase_letter}")
              |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
            '''

            result_phase = query_api.query(query_phase)

            for table in result_phase:
                for record in table.records:
                    power = record.get_value()
                    if power and power > 0:
                        phases_data.append((
                            record.get_time(),
                            'shelly_3em_entrada',
                            phase_name,
                            power,
                            None, None, None, None
                        ))

        logger.info(f"✓ Obtidos {len(phases_data)} registos de fases")

        # Inserir fases
        if phases_data:
            execute_batch(cursor, insert_query, phases_data, page_size=500)
            pg_conn.commit()
            logger.info(f"✓ Migrados {len(phases_data)} registos de fases")

        total_migrated = len(data) + len(phases_data)
        logger.info("=" * 70)
        logger.info(f"✅ Migração completa: {total_migrated} registos")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Erro durante migração: {e}")
        pg_conn.rollback()
    finally:
        cursor.close()
        pg_conn.close()
        influx_client.close()

if __name__ == "__main__":
    migrate()
