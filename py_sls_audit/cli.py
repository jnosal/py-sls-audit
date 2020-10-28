from datetime import datetime, timedelta
import json
import sys

import boto3
import botocore.exceptions
import click


class AWSBridge:
    def __init__(self, session):
        self.session = session
        self.functions = []
        self.metrics = []

    def fetch_functions(self):
        client = self.session.client("lambda")

        response = client.list_functions()
        self.functions = [fun.get("FunctionName") for fun in response.get("Functions")]
        for index, name in enumerate(self.functions):
            click.echo(f"{index + 1}. {name}")

    def get_configuration(self, index):
        function = self.functions[index]
        client = self.session.client("lambda")
        response = client.get_function_configuration(FunctionName=function)
        click.echo(json.dumps(response, indent=2))

    def fetch_metrics(self, index):
        function = self.functions[index]
        client = self.session.client("cloudwatch")

        response = client.list_metrics(
            Namespace="AWS/Lambda",
            Dimensions=[{"Name": "FunctionName", "Value": function}],
        )

        self.metrics = [metric.get("MetricName") for metric in response.get("Metrics")]
        self.metrics = sorted(set(self.metrics))
        for index, name in enumerate(self.metrics):
            click.echo(f"{index + 1}. {name}")

    def get_metric_statistics(self, function_index, metric_index):
        function = self.functions[function_index]
        metric = self.metrics[metric_index]
        client = self.session.client("cloudwatch")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        period = 60
        response = client.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName=metric,
            Dimensions=[{"Name": "FunctionName", "Value": function}],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=["Sum"],
        )
        print(response)
        return response


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

    proxy = AWSBridge(session=session)

    proxy.fetch_functions()
    function_index = prompt_for_index("function", len(proxy.functions))

    proxy.fetch_metrics(function_index)
    metric_index = prompt_for_index("metric", len(proxy.metrics))

    proxy.get_metric_statistics(function_index, metric_index)
