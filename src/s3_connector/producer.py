import boto3
import json
import uuid
from confluent_kafka import Producer

class S3Producer:
    def __init__(self, config):
        """
        Initializes the S3Producer.

        :param config: A dictionary with 'kafka' and 's3' configurations.
        """
        kafka_config = config.get("kafka", {})
        self.s3_config = config.get("s3", {})
        
        if "bucket" not in self.s3_config:
            raise ValueError("S3 bucket must be specified in the configuration.")

        self.kafka_producer = Producer(kafka_config)
        self.s3_client = boto3.client("s3")
        self.s3_bucket = self.s3_config["bucket"]

    def produce(self, topic, payload, key=None):
        """
        Uploads a large payload to S3 and sends a reference message to Kafka.

        :param topic: The Kafka topic to produce to.
        :param payload: The large message payload (bytes).
        :param key: The Kafka message key.
        """
        s3_key = str(uuid.uuid4())
        
        # Upload to S3
        response = self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=s3_key,
            Body=payload
        )
        
        # Get ETag for integrity check
        etag = response.get("ETag", "").strip('"')

        # Create reference message
        reference_message = {
            "s3_bucket": self.s3_bucket,
            "s3_key": s3_key,
            "etag": etag
        }
        
        # Produce message to Kafka
        self.kafka_producer.produce(
            topic,
            key=key,
            value=json.dumps(reference_message).encode('utf-8')
        )
        self.kafka_producer.flush()
