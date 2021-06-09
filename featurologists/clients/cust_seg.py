from kafka import KafkaConsumer
from json import loads, dumps
import pandas as pd

from featurologists.models.customer_segmentation import load_model, predict_proba


TOPIC_ONLINE_INPUT = "messes"


def consume_messages():
    consumer = KafkaConsumer(
        TOPIC_ONLINE_INPUT,
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: loads(x.decode('utf-8')))


    for message in consumer:
            message = message.value
            message = pd.DataFrame(message)
            print(message)

        # target_dir = '/home/godwin/Featurologists/models/customer_segmentation/xgboost'
        # model = 'model.pkl'

        # model = load_model(model, target_dir)
        # #print(model)

        # pred = predict_proba(model, message)
        # print(pred)