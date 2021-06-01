import json
import logging
import time
from typing import Optional

import kafka
from customer_segmentation_toolkit.data_zoo import download_data_csv


TOPIC_ONLINE_INPUT = "online-input"


def load_data():
    csv = "raw_live_data.csv"
    data = download_data_csv(f"data/output/01_data_split_offline_online/{csv}")
    data = data[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
        ]
    ]
    return data


def producer(kafka_endpoint: str, *, num_total: Optional[int] = None, delay_s: int = 4):
    producer = kafka.KafkaProducer(
        bootstrap_servers=[kafka_endpoint],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
    )

    df = load_data()
    total = df.shape[0]

    topic = TOPIC_ONLINE_INPUT
    for i, row in enumerate(df.iterrows(), 1):
        msg = row[1].tolist()
        logging.info(f"[{i}/{total}] Sending msg to '{topic}': {msg}")
        future = producer.send(topic=topic, value=msg)

        # Block for 'synchronous' sends
        try:
            future.get(timeout=10)
        except kafka.KafkaError as e:
            logging.error(f"Could not send message to kafka {topic}: {e}")
            raise
        producer.flush()

        if num_total is not None and i == num_total:
            break

        logging.info(f"Waiting {delay_s} sec")
        time.sleep(delay_s)

    logging.info("[+] Successfully finished")
