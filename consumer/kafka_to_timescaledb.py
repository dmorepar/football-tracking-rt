import json
import time
from confluent_kafka import Consumer, KafkaException
import psycopg2
from psycopg2.extras import execute_batch

# -------------------------------
# KAFKA CONFIG
# -------------------------------
KAFKA_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "positions_consumer",
    "auto.offset.reset": "earliest"
}

TOPIC = "players_topic"

# -------------------------------
# DB CONFIG (TimescaleDB)
# -------------------------------
DB_CONFIG = {
    "host": "localhost",
    "database": "football",
    "user": "postgres",
    "password": "postgres"
}

# -------------------------------
# Batch insert
# -------------------------------
def save_batch_to_db(batch, conn):
    if not batch:
        return
    sql = """
        INSERT INTO player_positions (team, player_id, role, game_state, timestamp, x_meters, y_meters, speed_mps)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (player_id, timestamp) DO NOTHING;
    """
    with conn.cursor() as cur:
        execute_batch(cur, sql, batch)
    conn.commit()

# -------------------------------
# MAIN
# -------------------------------
def main():
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe([TOPIC])

    conn = psycopg2.connect(**DB_CONFIG)

    print("Kafka ingestion → TimescaleDB started")

    batch = []
    BATCH_SIZE = 20  # Ajustable

    try:
        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())

                # JSON parser
                data = json.loads(msg.value().decode("utf-8"))

                batch.append((
                    data["team"],
                    data["player_id"],
                    data["role"],
                    data["game_state"],
                    data["timestamp"],  
                    data["x_meters"],
                    data["y_meters"],
                    data.get("speed_mps", None)
                ))

                if len(batch) >= BATCH_SIZE:
                    save_batch_to_db(batch, conn)
                    print(f"Saving {len(batch)} rows")
                    batch.clear()

            except json.JSONDecodeError as e:
                print("Decoding error:", e)
            except KafkaException as e:
                print("Error Kafka:", e)
                time.sleep(1)

    except KeyboardInterrupt:
        print("Consumer stopped...")

    finally:
        if batch:
            save_batch_to_db(batch, conn)
        consumer.close()
        conn.close()

if __name__ == "__main__":
    main()
