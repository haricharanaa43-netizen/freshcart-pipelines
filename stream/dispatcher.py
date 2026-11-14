import pika
import random
import json
import time
import uuid
import argparse
from datetime import datetime, timezone

EXCHANGE = "rapido-dispatch"

AMQP_URL = "amqp://guest:guest@localhost:5672/"

CITIES = ["bangalore", "chennai"]

ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "adyar", "velachery"]
}

TYPES = ["ride", "food"]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--demo-key",
        help="Publish one fixed routing key before random messages"
    )

    args = parser.parse_args()

    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True
    )

    print("Dispatcher started...")

    message_id = 1

    def publish(city, zone, request_type):
        nonlocal message_id

        routing_key = f"{city}.{zone}.{request_type}"

        message = {
            "id": str(uuid.uuid4()),
            "city": city,
            "zone": zone,
            "type": request_type,
            "ts": datetime.now(timezone.utc).isoformat()
        }

        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2
            )
        )

        print(f"Published: {routing_key} | {message}")

        message_id += 1

    # Optional deterministic message for assignment demonstration.
    if args.demo_key:
        parts = args.demo_key.split(".")

        if len(parts) != 3:
            raise ValueError("Routing key must have three words")

        publish(parts[0], parts[1], parts[2])

    try:
        while True:
            city = random.choice(CITIES)

            zone = random.choice(ZONES[city])

            request_type = random.choice(TYPES)

            publish(city, zone, request_type)

            time.sleep(2)

    except KeyboardInterrupt:
        print("Dispatcher stopped.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()