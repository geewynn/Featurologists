#from featurologists.clients.kafk_test import producer
from kafka import KafkaConsumer
from json import loads, dumps
import pandas as pd

#from featurologists.models.customer_segmentation import load_model, predict_proba


consumer = KafkaConsumer(
    'messes',
     bootstrap_servers=["localhost:9092"],
     group_id='group-1',
     max_poll_records=5,
     enable_auto_commit=False,
     value_deserializer=lambda x: loads(x.decode('utf-8')))


def process(batch_msgs):
    df = pd.DataFrame(batch_msgs)
    #df = df.values
    return df

def consume_messages():
    while True:
        message_batch = consumer.poll()

        for partition_batch in message_batch.values():
            for message in partition_batch:
                # do processing of message
                message = message.value
                #print(message)
                data = process(message)
                print(data)

        # commits the latest offsets returned by poll
        consumer.commit()

if __name__ == '__main__':
    consume_messages()
