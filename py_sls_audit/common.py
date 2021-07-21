from datetime import datetime, timedelta


class AWSBridge:
    def __init__(self, session):
        self.session = session
        self.functions = []
        self.metrics = []

    def fetch_functions(self):
        client = self.session.client("lambda")

        response = client.list_functions()
        self.functions = [fun.get("FunctionName") for fun in response.get("Functions")]
        return self.functions

    def fetch_metrics(self, index):
        function = self.functions[index]
        client = self.session.client("cloudwatch")

        response = client.list_metrics(
            Namespace="AWS/Lambda",
            Dimensions=[{"Name": "FunctionName", "Value": function}],
        )

        self.metrics = [metric.get("MetricName") for metric in response.get("Metrics")]
        self.metrics = sorted(set(self.metrics))
        return self.metrics

    def fetch_metric_statistics(self, function_index, metric_index):
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
        return response
