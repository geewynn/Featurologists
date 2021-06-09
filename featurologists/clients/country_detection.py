#from featurologists.clients.kafk_test import producer
from kafka import KafkaConsumer
from json import loads, dumps
import pandas as pd

#from featurologists.models.customer_segmentation import load_model, predict_proba


TOPIC_ONLINE_INPUT = "messes"


def process(batch_msgs):
    df = pd.DataFrame(batch_msgs)
    return df

def consume_messages():
    consumer = KafkaConsumer(
            TOPIC_ONLINE_INPUT,
            bootstrap_servers=["localhost:9092"],
            enable_auto_commit=False,
            value_deserializer=lambda x: loads(x.decode('utf-8')))

    batch = []

    for message in consumer:
        if len(batch) >= 10:
            # atomically store results of processing
            print([message_value for message_value in batch])
            batch = []

        # add result of message processing to batch
        batch.append(message.value)



if __name__ == '__main__':
    consume_messages()
