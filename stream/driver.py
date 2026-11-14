import pika
import json
import sys

EXCHANGE = "rapido-dispatch"

AMQP_URL = "amqp://guest:guest@localhost:5672/"


def main():

    if len(sys.argv) != 3:
        print("Usage: python driver.py NAME PATTERN")
        return

    name = sys.argv[1]
    pattern = sys.argv[2]

    params = pika.URLParameters(AMQP_URL)

    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True
    )

    # Create a private queue for each driver.
    result = channel.queue_declare(
        queue="",
        exclusive=True,
        auto_delete=True
    )

    queue_name = result.method.queue

    channel.queue_bind(
        exchange=EXCHANGE,
        queue=queue_name,
        routing_key=pattern
    )

    print(f"{name} started!")
    print(f"Binding pattern: {pattern}")
    print(f"Private queue: {queue_name}")
    print("Waiting for requests...\n")

    def callback(ch, method, properties, body):

        try:
            message = json.loads(body.decode())

            print(f"\n{name} received a request")
            print(f"Routing key: {method.routing_key}")
            print(f"Message: {message}")

            # Acknowledge successful processing.
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

            print(f"{name}: ACK sent")

        except Exception as e:

            print("Processing error:", e)

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )

    try:
        channel.start_consuming()

    except KeyboardInterrupt:
        print(f"\n{name} stopped.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()