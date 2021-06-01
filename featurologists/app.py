import logging

import typer

from .clients.kafka import producer


logging.basicConfig(level=logging.INFO)
from typing import Optional


app = typer.Typer()
client_app = typer.Typer()
model_app = typer.Typer()
feature_app = typer.Typer()

app.add_typer(client_app, name="client")
app.add_typer(model_app, name="model")
app.add_typer(feature_app, name="feature")


@client_app.command("run-kafka")
def client_run_kafka(
    endpoint: str = typer.Option(..., help="Kafka broker endpoint"),
    delay: int = typer.Option(4, help="Delay between messages in seconds"),
    num_total: Optional[int] = typer.Option(
        None, help="Number of total messages to send"
    ),
):
    """Run kafka client"""
    typer.echo(f"Running kafka client: endpoint={endpoint}")
    producer(endpoint, num_total=num_total, delay_s=delay)
