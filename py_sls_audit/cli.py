import boto3
import botocore.exceptions
import click

import sys


def list_functions(session):
    client = session.client("lambda")

    response = client.list_functions()
    for fun in response.get("Functions"):
        print(fun.get("FunctionName"))


@click.command()
@click.option("-p", "--profile", help="AWS profile to use.", required=True)
@click.option("-r", "--region", help="AWS region.", default="eu-west-1")
def run(profile, region):
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
    except botocore.exceptions.ProfileNotFound:
        print(f"Could not load profile {profile}")
        sys.exit(1)

    list_functions(session)
