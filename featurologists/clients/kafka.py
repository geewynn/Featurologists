import json
import time

from customer_segmentation_toolkit.data_zoo import download_data_csv
from kafka import KafkaProducer  # type: ignore
from tqdm import tqdm


def load_data():
    csv = "raw_live_data.csv"
    data = download_data_csv(f"data/output/01_data_split_offline_online/{csv}")

    columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
    ]
    data = data[columns]
    return data


def _iterrows_with_progress(df):
    yield from tqdm(df.iterrows(), total=df.shape[0])


def _iterrows_no_progress(df):
    yield from df.iterrows()


def iterate_data(df, progress: bool = False):
    if progress:
        iterrows = _iterrows_with_progress
    else:
        iterrows = _iterrows_no_progress
    for _, row in iterrows(df):
        yield list(row)


def producer(kafka_endpoint: str, progress: bool = False):
    producer = KafkaProducer(
        bootstrap_servers=[kafka_endpoint],
        api_version=(0, 10, 0),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    df = load_data()
    for row in iterate_data(df, progress=progress):
        print("sending message")
        producer.send(topic="messages", value=row)
        print("message sent, waiting 4s")
        time.sleep(4)
        producer.flush()
