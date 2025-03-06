import logging
import sqlite3
import os, datetime
from PyQt6.QtWidgets import QDialog, QComboBox, QLabel, QPushButton, QLineEdit, QDialogButtonBox
from PyQt6.QtWidgets import QFileDialog, QStyle,QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6 import uic
from astrodom.settings import *
from astrodom.loadSettings import *  # Import the constants



class Projects(QDialog):
    
    project_updated = pyqtSignal(int)
    
    def __init__(self, parent=None, project_id=None):
        super().__init__(parent)
        self.parent = parent
        self.project_id = project_id
        uic.loadUi((self.parent.rsc_path.joinpath( 'gui', 'projects.ui')), self)
        self.setWindowTitle("Projects")
        self.setGeometry(100, 100, 600, 300)
        self.infoBox = self.findChild(QLabel, 'infoBox')
        self.infoBox.setText("This dialog allows you to create or edit a project. Please provide the necessary details and click Save to store the project information.")
        
        self.project_name_input = self.findChild(QLineEdit, 'project_name_input')

        self.project_folder_input = self.findChild(QLineEdit, 'project_folder_input')
        self.browseButton = self.findChild(QPushButton, 'browseButton')

        self.project_dateComboBox = self.findChild(QComboBox, 'project_dateComboBox')
        current_year = datetime.datetime.now().year
        years = [str(year) for year in range(current_year, current_year - 11, -1)]
        self.project_dateComboBox.addItems(years)

        
        self.browseButton.clicked.connect(self.browse_folder)
        self.browseButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.project_statusComboBox = self.findChild(QComboBox, 'project_statusComboBox')
        self.project_statusComboBox.addItems(['Active', 'Archived'])

        self.delete_button = self.findChild(QPushButton, 'delete_button')
        self.buttonBox = self.findChild(QDialogButtonBox, 'buttonBox')

        self.buttonBox.accepted.connect(self.save_project)
        self.buttonBox.rejected.connect(self.close)

        self.delete_button.clicked.connect(self.delete_project)
        if not self.project_id:
            self.delete_button.setEnabled(False)

        if self.project_id is not None:
            self.load_project(self.project_id)


    def load_project(self, project_id):
        self.project_id = project_id

        # Connect to the database

        db_path = str(self.parent.rsc_path.joinpath( DBNAME))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch project data
        cursor.execute('SELECT name, base_dir, date, status FROM projects WHERE id = ?', (project_id,))
        project = cursor.fetchone()

        # Populate the form fields
        if project:
            self.project_name_input.setText(project[0])
            self.project_folder_input.setText(project[1])
            self.project_dateComboBox.setCurrentText(project[2])
            self.project_statusComboBox.setCurrentText(project[3])
        # Close the connection
        conn.close()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_folder_input.setText(folder)

    def save_project(self ):
        if not self.project_name_input.text().strip():
            logging.warning("Project name cannot be empty")
            return
        if not self.project_folder_input.text().strip():
            logging.warning("Project folder cannot be empty")
            return

        project_name = self.project_name_input.text()
        project_folder = self.project_folder_input.text()
        project_date = self.project_dateComboBox.currentText()

        project_status = self.project_statusComboBox.currentText()  

        # Connect to the database
        db_path = str(self.parent.rsc_path.joinpath( DBNAME))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if self.project_id is None:
            # Insert project data
            cursor.execute('''
                INSERT INTO projects (name, base_dir, date, status)
                VALUES (?, ?, ?, ?)
            ''', (project_name, project_folder, project_date, project_status))
            
            logging.info(f"Project {project_name} created")
            self.project_id = cursor.lastrowid
        else:
            # Update project data
            cursor.execute('''
                UPDATE projects
                SET name = ?, base_dir = ?, date = ?, status = ?
                WHERE id = ?
            ''', (project_name, project_folder, project_date,project_status,self. project_id))


        # Commit and close the connection
        conn.commit()
        conn.close()
        if project_status == 'Archived':
            self.project_updated.emit(0)
            logging.warning(f"Project {project_name} is now archived")
        else:   
            self.project_updated.emit(self.project_id)
            logging.info(f"Project {project_name} saved")

        self.accept()


    def delete_project(self):
            
            if self.project_id is None:
                logging.warning("No project selected for deletion")
                return
            reply = QMessageBox.question(self, 'Confirmation', 
            'Are you sure you want to delete this project and associated images from the database? \nThis action cannot be undone. \nNo file will be delete from the filesystem.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
            # Connect to the database
            db_path = str(self.parent.rsc_path.joinpath( DBNAME))
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Delete project data from projects table
            try:
                cursor.execute('DELETE FROM projects WHERE id = ?', (self.project_id,))

            except sqlite3.Error as e:
                logging.error(f"Error deleting project: {e}")
                conn.rollback()
                return
            
            logging.info("Project deleted")
            
            # Delete related images from images table
            try:
                cursor.execute('DELETE FROM images WHERE project_id = ?', (self.project_id,))
            except sqlite3.Error as e:
                logging.error(f"Error deleting images: {e}")
                conn.rollback()
                return

            logging.info("Images deleted")

            # Commit and close the connection
            conn.commit()
            conn.close()

            self.project_updated.emit(0)
            self.accept()
