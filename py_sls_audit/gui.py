import py_cui


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.set_title("SLS AUDIT")

        self.root.set_status_bar_text("Quit - q | Refresh - r")

        self.list_functions_menu = self.root.add_scroll_menu(
            "Functions", 0, 0, row_span=7, column_span=2
        )
        self.list_functions_menu.set_border_color(py_cui.GREEN_ON_BLACK)

        self.metrics_block = self.root.add_text_block(
            "Metric", 0, 2, row_span=7, column_span=6, initial_text="***"
        )

        # Textboxes for new branches and commits
        self.period_textbox = self.root.add_text_box("Period", 7, 0, column_span=2)
        self.phrase_textbox = self.root.add_text_box("Phrase", 8, 0, column_span=2)
        self.status_message_box = self.root.add_text_block(
            "Status", 7, 2, column_span=6, row_span=2, initial_text="***"
        )


def run():
    root = py_cui.PyCUI(9, 8)
    root.toggle_unicode_borders()

    GUI(root)
    root.start()
