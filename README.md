# Kafka S3 Connector (`kaf-s3-connector`)

A Python library to seamlessly handle large Kafka messages by offloading them to Amazon S3.

This library provides a custom Kafka Producer and Consumer that automatically handle the process of storing large message payloads in an S3 bucket and passing lightweight references through Kafka.

## Key Features

-   **Automatic S3 Offloading:** Produce messages larger than Kafka's recommended limit without manual intervention.
-   **Transparent Consumption:** Consume large messages as if they were directly in Kafka.
-   **Data Integrity:** Verifies the integrity of S3 objects using ETags to prevent data corruption.
-   **Secure by Default:** Leverages AWS IAM roles and the default `boto3` credential chain, avoiding the need to hardcode secrets.
-   **Flexible Configuration:** Built on top of `confluent-kafka-python`, allowing for full customization of Kafka client settings, including SASL and SSL.

## Installation

```bash
pip install .
```

## How it Works

1.  The `S3Producer` receives a large payload.
2.  It uploads the payload to a specified S3 bucket with a unique key.
3.  It produces a small JSON message to a Kafka topic containing the S3 bucket, key, and the object's ETag.
4.  The `S3Consumer` reads the JSON reference from Kafka.
5.  It downloads the original payload from S3.
6.  It verifies the ETag to ensure the data is not corrupted, then returns the payload to your application.

## Configuration

Configuration is handled through a single dictionary, with separate keys for `kafka` and `s3` settings.

### Security

-   **AWS Credentials:** This library is designed to be secure. **Do not** pass AWS credentials in the configuration. It uses `boto3`'s default credential discovery chain. The recommended and most secure way to provide credentials is by using an **IAM Role** attached to your compute instance (EC2, ECS, Lambda, etc.). Alternatively, you can use environment variables or a shared credentials file (`~/.aws/credentials`).
-   **Kafka Security:** All standard `confluent-kafka-python` security settings are supported and should be passed within the `kafka` dictionary. This includes SASL for authentication (e.g., `PLAIN`, `SCRAM`, and `GSSAPI` for **Kerberos**) and SSL/TLS for encryption.

### Example Configuration

```python
producer_config = {
    "kafka": {
        "bootstrap.servers": "localhost:9092",
    },
    "s3": {
        "bucket": "my-large-messages-bucket",
    }
}

consumer_config = {
    "kafka": {
        "bootstrap.servers": "localhost:9092",
        "group.id": "my-s3-consumers",
        "auto.offset.reset": "earliest",
    },
    "s3": {
        "bucket": "my-large-messages-bucket",
    }
}
```

## Usage

### Producer

```python
from s3_connector import S3Producer

# Initialize producer with the config
producer = S3Producer(config=producer_config)

# Read a sample file
with open("examples/sample_payload.txt", "rb") as f:
    payload_data = f.read()

# Produce the data to a topic
producer.produce(topic="large-messages-topic", payload=payload_data)
print("Produced message to Kafka via S3.")
```

### Consumer

```python
from s3_connector import S3Consumer

# Initialize consumer with the config
consumer = S3Consumer(config=consumer_config)
consumer.subscribe(["large-messages-topic"])

print("Waiting for messages...")
while True:
    try:
        # Poll for a message
        payload = consumer.poll(timeout=10.0)

        if payload:
            print(f"Received message of size: {len(payload)} bytes")
            # Save the received file
            with open("examples/received_payload.txt", "wb") as f:
                f.write(payload)
            break # Exit after one message for this example

    except KeyboardInterrupt:
        break

consumer.close()

## Testing

To run the unit tests for this library, first install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Then, run `pytest` from the root of the project:

```bash
pytest
```
