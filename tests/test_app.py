from typer.testing import CliRunner

from featurologists.app import app


def test_app():
    runner = CliRunner()
    args = ["client", "run-kafka"]
    result = runner.invoke(app, args)
    assert result.exit_code == 2
    assert "Error: Missing option '--endpoint'" in result.output, result.output
