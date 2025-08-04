import json
import pytest
from unittest.mock import MagicMock
from s3_connector import S3Consumer, DataIntegrityError

@pytest.fixture
def consumer_config():
    return {
        "kafka": {
            "bootstrap.servers": "mock:9092",
            "group.id": "test-group",
            "test.mock.num.brokers": 3
        },
        "s3": {"bucket": "test-bucket"}
    }

def test_consumer_init(mocker, consumer_config):
    """Tests the initialization of the S3Consumer."""
    mocker.patch("s3_connector.consumer.boto3")
    mocker.patch("s3_connector.consumer.Consumer")
    
    consumer = S3Consumer(consumer_config)
    
    assert consumer.kafka_consumer is not None
    assert consumer.s3_client is not None

def test_poll_message(mocker, consumer_config):
    """Tests polling and successfully retrieving a message."""
    mock_boto3 = mocker.patch("s3_connector.consumer.boto3")
    mock_kafka_consumer_class = mocker.patch("s3_connector.consumer.Consumer")
    mock_kafka_consumer_instance = mock_kafka_consumer_class.return_value

    # Mock Kafka message
    ref_message = {
        "s3_bucket": "test-bucket",
        "s3_key": "test-key",
        "etag": "12345"
    }
    kafka_msg = MagicMock()
    kafka_msg.value.return_value = json.dumps(ref_message).encode('utf-8')
    kafka_msg.error.return_value = None
    mock_kafka_consumer_instance.poll.return_value = kafka_msg

    # Mock S3 response
    s3_payload = b"This is the payload from S3"
    mock_s3_response = {
        "Body": MagicMock(),
        "ETag": '"12345"'
    }
    mock_s3_response["Body"].read.return_value = s3_payload
    mock_boto3.client.return_value.get_object.return_value = mock_s3_response

    consumer = S3Consumer(consumer_config)
    payload = consumer.poll()

    assert payload == s3_payload
    mock_boto3.client.return_value.get_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")

def test_poll_data_integrity_error(mocker, consumer_config):
    """Tests that DataIntegrityError is raised on ETag mismatch."""
    mock_boto3 = mocker.patch("s3_connector.consumer.boto3")
    mock_kafka_consumer_class = mocker.patch("s3_connector.consumer.Consumer")
    mock_kafka_consumer_instance = mock_kafka_consumer_class.return_value

    # Mock Kafka message with a different ETag
    ref_message = {
        "s3_bucket": "test-bucket",
        "s3_key": "test-key",
        "etag": "expected-etag"
    }
    kafka_msg = MagicMock()
    kafka_msg.value.return_value = json.dumps(ref_message).encode('utf-8')
    kafka_msg.error.return_value = None
    mock_kafka_consumer_instance.poll.return_value = kafka_msg

    # Mock S3 response with a mismatched ETag
    mock_s3_response = {"ETag": '"actual-etag"'}
    mock_boto3.client.return_value.get_object.return_value = mock_s3_response

    consumer = S3Consumer(consumer_config)
    
    with pytest.raises(DataIntegrityError):
        consumer.poll()
