"""Basic CLI smoke tests."""

from click.testing import CliRunner

from ace.cli import cli


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ACE" in result.output


def test_generate_subcommand_exists() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--spec" in result.output


def test_curate_subcommand_exists() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["curate", "--help"])
    assert result.exit_code == 0
    assert "--path" in result.output


def test_reflect_subcommand_exists() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["reflect", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.output
