import json
import csv
from kafka import KafkaProducer
import time
import argparse
from customer_segmentation_toolkit.data_zoo import download_data_csv


def load_data():
    columns =['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']

    csv = "raw_live_data.csv"
    data = download_data_csv(
            f"data/output/01_data_split_offline_online/{csv}"
        )
    return columns, data


def producer(arg=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', help='kafka bootstrap broker')
    known_args, _ = parser.parse_known_args(arg)

    columns, data = load_data()

    producer = KafkaProducer(
        bootstrap_servers=[known_args.endpoint],
        api_version=(0,10,0),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for _, row in data.iterrows():
        print("sending message")
        producer.send(topic='messages', value=[row[x] for x in columns])
        print("message sent, waiting 4s")
        print(time.sleep(4))
        producer.flush()

producer()