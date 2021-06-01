import typer


app = typer.Typer()
client_app = typer.Typer()
model_app = typer.Typer()
feature_app = typer.Typer()

app.add_typer(client_app, name="client")
app.add_typer(model_app, name="model")
app.add_typer(feature_app, name="feature")


@client_app.command("run-kafka")
def client_run_kafka(endpoint: str):
    """Run kafka client"""
    typer.echo(f"Running kafka client: endpoint={endpoint}")
