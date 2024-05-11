import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QProgressBar,
    QRadioButton,
    QHeaderView,
    QSpacerItem,
    QSizePolicy,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Widget Interface")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Person Name", "Online Profile"])
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Set column widths
        self.table.setColumnWidth(0, 300)  # Width of the Person Name column

        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # Stretch Person Name column

        # Radio buttons
        radio_layout = QHBoxLayout()
        self.active_radio = QRadioButton("Active")
        self.inactive_radio = QRadioButton("Inactive")
        radio_layout.addWidget(self.active_radio)
        radio_layout.addWidget(self.inactive_radio)
        layout.addLayout(radio_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Make non-editable
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Pagination controls
        self.pagination_layout = QHBoxLayout()
        layout.addLayout(self.pagination_layout)

        # Current page label
        self.current_page_label = QLabel()
        self.pagination_layout.addWidget(self.current_page_label)

    def addPaginationControls(self, prev_callback, next_callback):
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(prev_callback)
        self.pagination_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(next_callback)
        self.pagination_layout.addWidget(next_button)

    def updatePageLabel(self, current_page, total_pages):
        self.current_page_label.setText(f"Page {current_page} / {total_pages}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
