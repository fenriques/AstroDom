import os,shutil, importlib_resources,sqlite3
from PyQt6.QtWidgets import QTextEdit, QDialog, QGridLayout, QLabel, QComboBox, QLineEdit, QFileDialog, QPushButton,QMessageBox, QStyle
from PyQt6.QtCore import pyqtSignal
from astrodom.loadSettings import *  
from PyQt6.QtSql import QSqlDatabase, QSqlQuery


class FileOperationDialog(QDialog):
    filesDeleted = pyqtSignal()

    def __init__(self, files, parent=None):
        super(FileOperationDialog, self).__init__(parent)
        self.files = files
        self.initUI()
        self.rsc_path = importlib_resources.files("astrodom").joinpath('rsc')

    def initUI(self):
        self.setWindowTitle("File Operation")
        self.setGeometry(100, 100, 800, 400)

        layout = QGridLayout()

        # Images ComboBox
        selected_images_label = QLabel("With Selected Images:")
        layout.addWidget(selected_images_label, 0, 0)

        self.selectedImagesComboBox = QComboBox()
        # copying rejected files is not useful, so it is removed from the options
        self.selectedImagesComboBox.addItems(["Move to",  "Delete"])
        #self.selectedImagesComboBox.addItems(["Move to", "Copy to", "Delete"])
        layout.addWidget(self.selectedImagesComboBox, 0, 1)

        # Directory Select Edit
        self.directorySelectEdit = QLineEdit()
        self.directorySelectEdit.setPlaceholderText("Select Destination Folder")
        layout.addWidget(self.directorySelectEdit, 1, 0)

        # Directory Select Button
        self.directorySelectButton = QPushButton("Browse")
        self.directorySelectButton.clicked.connect(self.selectDirectory)
        layout.addWidget(self.directorySelectButton, 1, 1)

        # Apply
        applyButton = QPushButton("Apply")
        applyButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        applyButton.clicked.connect(self.applyOperation)

        layout.addWidget(applyButton, 2, 1)

        # Log the number of files
        num_files_label = QLabel(f"Number of selected images: {len(self.files)}")
        layout.addWidget(num_files_label, 3, 0, 1, 2)

        # Files Text Area
        self.filesTextArea = QTextEdit()
        self.filesTextArea.setReadOnly(True)
        self.filesTextArea.setText("\n".join(self.files))
        layout.addWidget(self.filesTextArea, 4, 0, 1, 2)
        self.setLayout(layout)

    def selectDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if directory:
            self.directorySelectEdit.setText(directory)


    def applyOperation(self):
        operation = self.selectedImagesComboBox.currentText()
        destination = self.directorySelectEdit.text()
        if operation in ["Move to", "Copy to"] and not destination:
            raise ValueError("Select a destination folder")

        match operation:
            case "Move to":
                self.filesTextArea.clear()
                try:
                    for file in self.files:
                        shutil.move(file, os.path.join(destination, os.path.basename(file)))
                        self.filesTextArea.append(f"Moved: {file}")

                    self.filesTextArea.append(f"Files moved successfully. Total files moved: {len(self.files)}")
                    self.delete_file_from_db()
                    self.filesDeleted.emit()  

                except Exception as e:
                    self.filesTextArea.append(f"Error moving files: {e}")
        
        
            case "Copy to":
                self.filesTextArea.clear()
                try:
                    for file in self.files:
                        shutil.copy(file, os.path.join(destination, os.path.basename(file)))
                        self.filesTextArea.append(f"Copied: {file}")
                    self.filesTextArea.append(f"Files copied successfully. Total files copied: {len(self.files)}")
                    self.delete_file_from_db()
                    self.filesDeleted.emit()

                except Exception as e:
                    self.filesTextArea.append(f"Error copying files: {e}")

            case "Delete":

                reply = QMessageBox.question(self, 'Confirm Delete', 
                                             f"Are you sure you want to delete {len(self.files)} files?", 
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
            
                    self.filesTextArea.clear()
                    try:
                        for file in self.files:
                            os.remove(file)
                            self.filesTextArea.append(f"Deleted: {file}")
                        self.filesTextArea.append(f"Files deleted successfully. Total files deleted: {len(self.files)}")
                        self.delete_file_from_db()
                        self.filesDeleted.emit() 

                    except Exception as e:
                        self.filesTextArea.append(f"Error deleting files: {e}")

    def delete_file_from_db(self):
        db_path = str(self.rsc_path.joinpath(DBNAME))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            for file in self.files:
                cursor.execute("DELETE FROM images WHERE FILE = ?", (file,))

            self.filesTextArea.append(f"Files deleted from database successfully. Total files deleted: {len(self.files)}")
        except Exception as e:
            self.filesTextArea.append(f"Error deleting files from database: {e}")
        finally:

            conn.commit()
            conn.close()
    
