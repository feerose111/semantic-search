import json
from confluent_kafka import Producer

with open('F:/internship/ai-search/data/esewa_dataset.json', "r", encoding="utf-8") as f:
    dataset = json.load(f)

producer = Producer({'bootstrap.servers': 'localhost:9092'})

for category in dataset:
    for item in dataset[category]:
        producer.produce(
            topic = "esewa_docs",
            value = json.dumps(item).encode('utf-8')
        )
        print(f"✅ Sent to Kafka: {item['id']}")

producer.flush()