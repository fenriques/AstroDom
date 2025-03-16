from PyQt6.QtWidgets import  QDialog,QHBoxLayout
import os,  logging
from PyQt6.QtSql import QSqlQuery
from PyQt6.QtWidgets import QVBoxLayout,QPushButton,QSizePolicy,QLabel, QMessageBox,QStyle
from astrodom.previewAndDataWidget import PreviewAndDataWidget

# This class is a dialog that allows the user to check FITS files in the project folder
# and eventually delete them.
# It relies on the PreviewAndDataWidget class to display the FITS files.
class BlinkDialog(QDialog):
    def __init__(self, project_id,parent=None):
        super().__init__(parent)
        self.parent = parent
        self.project_id = project_id

        logging.debug("Opening open_blink_dialog")
        # Find all FITS files in the project base folder and subfolders
        query = QSqlQuery()
        query.prepare("SELECT BASE_DIR FROM projects WHERE ID = :id ORDER BY DATE DESC")
        query.bindValue(":id",self.project_id)

        if query.exec() and query.next():
            base_directory = query.value(0)
        self.fits_files = []
        for root, dirs, files in os.walk(base_directory):
            for file in files:
                if file.lower().endswith(('.fits', '.fit')):
                    self.fits_files.append(os.path.join(root, file))


        self.setWindowTitle("Blink Dialog")

        self.file_name_label = QLabel(self)

        self.previewWidget = PreviewAndDataWidget(previewWidth=760)
        self.previewWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        delete_button = QPushButton("Delete", self)
        delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        delete_button.clicked.connect(self.delete_item)

        self.current_fits_index = 0
        prev_button = QPushButton("Previous", self)
        prev_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        next_button = QPushButton("Next", self)
        next_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))

        prev_button.clicked.connect(self.prev_item)
        next_button.clicked.connect(self.next_item)

        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)
        
        layout = QVBoxLayout()
        layout.addWidget(self.file_name_label)
        layout.addWidget(self.previewWidget)
        layout.addWidget(delete_button)
        layout.addLayout(button_layout)
        
        self.update_preview()
        self.setLayout(layout)

    def update_preview(self):
        if self.fits_files:
            self.file_name_label.setText(os.path.basename(self.fits_files[self.current_fits_index]))
            self.previewWidget.setBlinkItem(self.fits_files[self.current_fits_index])

    def prev_item(self):
        if self.current_fits_index > 0:
            self.current_fits_index -= 1
            self.update_preview()

    def next_item(self):
        if self.current_fits_index < len(self.fits_files) - 1:
            self.current_fits_index += 1
            self.update_preview()
        
    def delete_item(self):
        if self.fits_files:
            reply = QMessageBox.question(self, 'Delete Confirmation', 
                    f"Are you sure you want to delete {os.path.basename(self.fits_files[self.current_fits_index])}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
            file_to_delete = self.fits_files.pop(self.current_fits_index)
            
            try:
                os.remove(file_to_delete)
                logging.info(f"Deleted {file_to_delete}")
            except Exception as e:
                logging.error(f"Error deleting {file_to_delete}: {e}")  
                
            if self.current_fits_index >= len(self.fits_files):
                self.current_fits_index = len(self.fits_files) - 1
            self.update_preview()
