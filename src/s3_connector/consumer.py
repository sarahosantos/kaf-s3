import boto3
import json
from confluent_kafka import Consumer, KafkaError
from .exceptions import DataIntegrityError

class S3Consumer:
    def __init__(self, config):
        """
        Initializes the S3Consumer.

        :param config: A dictionary with 'kafka' and 's3' configurations.
        """
        kafka_config = config.get("kafka", {})
        self.s3_config = config.get("s3", {})

        if "group.id" not in kafka_config:
            raise ValueError("Kafka consumer 'group.id' must be specified.")

        self.kafka_consumer = Consumer(kafka_config)
        self.s3_client = boto3.client("s3")

    def close(self):
        """
        Closes the Kafka consumer.
        """
        self.kafka_consumer.close()

    def subscribe(self, topics):
        """
        Subscribes the consumer to a list of topics.
        """
        self.kafka_consumer.subscribe(topics)

    def poll(self, timeout=1.0):
        """
        Polls for a message, downloads the payload from S3, and returns it.

        :param timeout: The maximum time to block waiting for a message.
        :return: The downloaded payload (bytes) or None if no message.
        """
        msg = self.kafka_consumer.poll(timeout)

        if msg is None:
            return None
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                return None
            else:
                raise Exception(msg.error())

        try:
            ref_message = json.loads(msg.value().decode('utf-8'))
            s3_bucket = ref_message["s3_bucket"]
            s3_key = ref_message["s3_key"]
            expected_etag = ref_message.get("etag")

            # Download from S3
            response = self.s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            
            # Verify ETag for data integrity
            actual_etag = response.get("ETag", "").strip('"')
            if expected_etag and actual_etag != expected_etag:
                raise DataIntegrityError(f"Data integrity check failed for S3 object {s3_key}")

            return response["Body"].read()

        except (json.JSONDecodeError, KeyError) as e:
            # Handle malformed messages
            print(f"Skipping malformed message: {e}")
            return None
