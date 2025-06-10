import json
from confluent_kafka import Consumer
from pymilvus import Collection, connections
from sentence_transformers import SentenceTransformer
from backend.utils.config import MILVUS_HOST, MILVUS_PORT

# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
collection = Collection("esewa_docs")
collection.load()

model = SentenceTransformer("all-MiniLM-L6-v2")

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'esewa_consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(["esewa_docs"])

print("✅ Listening to Kafka...")


try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"⚠️ Kafka error: {msg.error()}")
            continue


        data = json.loads(msg.value().decode('utf-8'))

        doc_type = data.get("type")
        if doc_type == "transaction":
            text = f"{data['description']} {data.get('merchant_name', '')}"
        elif doc_type == "saved_payment":
            text = f"{data['description']} {data.get('payee_name', '')}"
        elif doc_type == "service":
            text = data.get("content", "")
        elif doc_type == "product":
            text = f"{data['description']} {data.get('product_name', '')}"
        else:
            continue

        embedding = model.encode(text).tolist()
        try:
            collection.insert([
                [data["id"]],
                [embedding],
                [data]
            ])
            print(f"✅ Inserted: {data['id']}")
        except Exception as e:
            print(f"⚠️ Failed to insert {data['id']}: {e}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()