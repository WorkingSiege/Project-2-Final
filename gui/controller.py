import os
import sys
import json
import math
import threading
import webbrowser
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QPushButton
from gui.mainWindow import MainWindow
from multiprocessing import Manager, Queue
from crawler.crawler import DirectoryCrawler


class Controller(QObject):
    studentReady = pyqtSignal(object)  # Signal to emit when a student is ready
    progressUpdated = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.window.show()

        self.students = []

        # Pagination settings
        self.page_size = 50
        self.current_page = 1

        # Crawler & statistics
        self.manager = Manager()
        self.crawler_stats = self.manager.dict()
        self.crawler_stats["surnames"] = 0
        self.crawler_stats["surnamesProcessed"] = 0
        self.profile_queue = Queue()
        self.crawler = DirectoryCrawler(self.crawler_stats, self.profile_queue)

        f_stop = threading.Event()
        self.pollStudents(f_stop)

        # Crawler/PyQT progress bar
        f_stop2 = threading.Event()
        self.pollProgress(f_stop2)

        # Connect signals to associated methods
        self.studentReady.connect(self.addStudentRow)
        self.progressUpdated.connect(self.updateProgress)

        # Populate table with sample data
        self.populateTable()

        # Connect widget functions
        self.window.search_input.textChanged.connect(self.search)
        self.window.active_radio.toggled.connect(self.toggleCrawler)

        self.setupPaginationControls()

        sys.exit(self.app.exec())

    def maxPage(self, total_students=None):
        max_page = math.ceil((total_students or len(self.students)) / self.page_size)
        if max_page == 0:
            return 1
        return math.ceil((total_students or len(self.students)) / self.page_size)

    def setupPaginationControls(self):
        def showPreviousPage():
            if self.current_page > 1:
                self.current_page -= 1
                self.window.table.clearContents()
                self.populateTable()

        def showNextPage():
            max_page = self.maxPage()
            if self.current_page < max_page:
                self.current_page += 1
                self.window.table.clearContents()
                self.populateTable()

        self.window.addPaginationControls(showPreviousPage, showNextPage)

    def toggleCrawler(self, startCrawler):
        if startCrawler:
            # Starting crawler
            self.crawler.start()
        else:
            # Stopping crawler
            self.crawler.stop()

    def pollStudents(self, f_stop):
        while not self.profile_queue.empty():
            student = self.profile_queue.get()
            self.studentReady.emit(
                {
                    "student": student,
                }
            )
        if not f_stop.is_set():
            threading.Timer(1, self.pollStudents, [f_stop]).start()

    def pollProgress(self, f_stop):
        progress = math.floor(self.crawler.getProgress())
        self.progressUpdated.emit(progress)
        if not f_stop.is_set():
            threading.Timer(1, self.pollProgress, [f_stop]).start()

    def populateTable(self):
        students = []
        students_path = "output/students.jsonl"
        if os.path.isfile(students_path):
            with open(students_path, "r") as input_file:
                studentsLines = input_file.read().splitlines()
                for student in studentsLines:
                    students.append(json.loads(student))

        self.window.table.setRowCount(0)
        self.students = students
        self.window.updatePageLabel(self.current_page, self.maxPage(len(students)))

        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, len(students))
        for student in students[start_index:end_index]:
            self.studentReady.emit({"student": student, "initial_load": True})

    def updateProgress(self, progress):
        self.window.progress_bar.setValue(progress)

    def addStudentRow(self, payload):
        student = payload["student"]
        initial_load = "initial_load" in payload and payload["initial_load"]
        if not initial_load:
            if student not in self.students:
                self.students.append(student)
            self.window.updatePageLabel(self.current_page, self.maxPage())
        row_position = 0  # Add to the top, versus self.window.table.rowCount()
        self.window.table.insertRow(row_position)
        name_item = QTableWidgetItem(student["name"])
        self.window.table.setItem(row_position, 0, name_item)
        button_item = QPushButton("View Profile")
        button_item.clicked.connect(lambda: webbrowser.open(student["profile_url"]))
        self.window.table.setCellWidget(row_position, 1, button_item)
        self.window.table.removeRow(self.page_size)

    def search(self):
        search_text = self.window.search_input.text().lower()

        # Using filter function
        filtered_students = list(
            filter(lambda d: search_text.lower() in d["name"].lower(), self.students)
        )

        self.current_page = 1
        self.window.table.setRowCount(0)

        for student in filtered_students[: self.page_size]:
            self.studentReady.emit(
                {
                    "student": student,
                }
            )

        self.window.updatePageLabel(
            self.current_page, self.maxPage(len(filtered_students))
        )
