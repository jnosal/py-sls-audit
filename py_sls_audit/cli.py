import json
import sys

import boto3
import botocore.exceptions
import click

from .common import AWSBridge

_COMMANDS = ["metrics", "conf", "exit"]


class CLIAwsProxy(AWSBridge):

    def fetch_and_list_functions(self):
        data = self.fetch_functions()

        for index, name in enumerate(data):
            click.echo(f"{index + 1}. {name}")

    def fetch_and_list_metrics(self, index):
        data = self.fetch_metrics(index)
        for index, name in enumerate(data):
            click.echo(f"{index + 1}. {name}")

    def fetch_and_list_metric_statistics(self, function_index, metric_index):
        data = self.fetch_metric_statistics(function_index, metric_index)
        click.echo(json.dumps(data, indent=2))

    def command_exit(self, *args):
        sys.exit(1)

    def command_conf(self, index):
        function = self.functions[index]
        client = self.session.client("lambda")
        response = client.get_function_configuration(FunctionName=function)
        click.echo(json.dumps(response, indent=2))

    def command_metrics(self, index):
        self.fetch_and_list_metrics(index)

        if len(self.metrics) < 1:
            return

        metric_index = prompt_for_index("metric", len(self.metrics))
        self.fetch_and_list_metric_statistics(index, metric_index)


def prompt_for_index(name, total):
    index = click.prompt(f"Please enter {name} index", type=int)

    if index < 1 or index > total:
        click.echo(f"Index must be between 1 and {total}")
        return prompt_for_index(name, total)

    return index - 1


@click.command()
@click.option("-p", "--profile", help="AWS profile to use.", required=True)
@click.option("-r", "--region", help="AWS region.", default="eu-west-1")
def run(profile, region):
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
    except botocore.exceptions.ProfileNotFound:
        click.echo(f"Could not load profile {profile}")
        sys.exit(1)

    proxy = CLIAwsProxy(session=session)

    proxy.fetch_and_list_functions()
    function_index = prompt_for_index("function", len(proxy.functions))
    click.clear()

    while True:
        choice = click.prompt(
            "Please enter command to run", type=click.Choice(_COMMANDS)
        )
        click.clear()
        getattr(proxy, f"command_{choice}")(function_index)
        click.echo("")
