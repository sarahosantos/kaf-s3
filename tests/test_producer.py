import json
import pytest
from s3_connector import S3Producer

@pytest.fixture
def producer_config():
    return {
        "kafka": {
            "bootstrap.servers": "mock:9092",
            "test.mock.num.brokers": 3
        },
        "s3": {"bucket": "test-bucket"}
    }

def test_producer_init(mocker, producer_config):
    """Tests the initialization of the S3Producer."""
    mocker.patch("s3_connector.producer.boto3")
    mocker.patch("s3_connector.producer.Producer")
    
    producer = S3Producer(producer_config)
    
    assert producer.s3_bucket == "test-bucket"
    assert producer.kafka_producer is not None
    assert producer.s3_client is not None

def test_produce_message(mocker, producer_config):
    """Tests the produce method."""
    mock_boto3 = mocker.patch("s3_connector.producer.boto3")
    mock_kafka_producer_class = mocker.patch("s3_connector.producer.Producer")
    mock_kafka_producer_instance = mock_kafka_producer_class.return_value

    # Mock the S3 response
    mock_boto3.client.return_value.put_object.return_value = {"ETag": '"12345"'}

    producer = S3Producer(producer_config)
    
    payload = b"This is a test payload"
    topic = "test-topic"
    
    producer.produce(topic, payload)

    # Assert S3 call
    mock_boto3.client.return_value.put_object.assert_called_once()
    args, kwargs = mock_boto3.client.return_value.put_object.call_args
    assert kwargs["Bucket"] == "test-bucket"
    assert kwargs["Body"] == payload
    
    # Assert Kafka call
    mock_kafka_producer_instance.produce.assert_called_once()
    args, kwargs = mock_kafka_producer_instance.produce.call_args
    assert args[0] == topic
    
    # Verify the content of the Kafka message
    ref_message = json.loads(kwargs["value"].decode('utf-8'))
    assert ref_message["s3_bucket"] == "test-bucket"
    assert ref_message["etag"] == "12345"
    assert "s3_key" in ref_message

    mock_kafka_producer_instance.flush.assert_called_once()
