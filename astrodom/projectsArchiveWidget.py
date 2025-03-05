import sys
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
import sqlite3

class ProjectsArchiveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Projects Archive')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.loadProjects()

    def loadProjects(self):
        connection = sqlite3.connect('projects.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        connection.close()

        self.tableWidget.setRowCount(len(projects))
        self.tableWidget.setColumnCount(len(projects[0]) if projects else 0)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Name', 'Description', 'Start Date', 'End Date'])

        for row_idx, project in enumerate(projects):
            for col_idx, data in enumerate(project):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

