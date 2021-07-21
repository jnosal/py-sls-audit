import sys

import boto3
import botocore.exceptions
import click
import py_cui
from py_cui import ui
import threading

from .common import AWSBridge

# Make read only text blocks
ui.TextBlockImplementation._handle_newline = lambda x: None
ui.TextBlockImplementation._handle_backspace = lambda x: None

_PERIODS = [
    "15m",
    "30m",
    "1h",
    "3h",
    "12h",
]


class GUI:
    def __init__(self, root, proxy: AWSBridge):
        self.proxy = proxy
        self.proxy.fetch_functions()

        self.root = root
        self.root.set_title("SLS AUDIT")

        self.root.set_status_bar_text("Quit - q | Refresh - r")

        self.list_functions_menu = self.root.add_scroll_menu(
            "Functions", 0, 0, row_span=5, column_span=2
        )
        self.list_functions_menu.add_key_command(py_cui.keys.KEY_ENTER, self.select_function)
        self.list_functions_menu.add_item_list(self.proxy.functions)

        self.metrics_menu = self.root.add_scroll_menu(
            "Metric", 5, 0, row_span=2, column_span=2,
        )

        # Textboxes for new branches and commits
        self.period_textbox = self.root.add_scroll_menu(
            "Period", 7, 0, column_span=2, row_span=2
        )
        self.phrase_textbox = self.root.add_text_box(
            "Phrase", 0, 2, column_span=6, initial_text="Search..."
        )
        self.status_message_box = self.root.add_text_block(
            "Status", 1, 2, column_span=6, row_span=8, initial_text="***"
        )

        elements = [
            self.list_functions_menu,
            self.metrics_menu,
            self.period_textbox,
            self.phrase_textbox,
            self.status_message_box,
        ]

        for element in elements:
            element.set_border_color(py_cui.GREEN_ON_BLACK)

        self.period_textbox.add_item_list(_PERIODS)

    def _select_function(self):
        index = self.list_functions_menu.get_selected_item_index()
        metrics = self.proxy.fetch_metrics(index)
        self.metrics_menu.add_item_list(metrics)
        self.root.stop_loading_popup()

    def select_function(self):
        self.root.show_loading_icon_popup('Please Wait', 'Loading')
        self.metrics_menu.clear()
        thread = threading.Thread(target=self._select_function)
        thread.start()


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

    root = py_cui.PyCUI(9, 8)
    root.toggle_unicode_borders()

    GUI(root, proxy)
    root.start()
