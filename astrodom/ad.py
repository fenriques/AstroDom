import os, sys, logging

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,QPushButton,QComboBox,QTextEdit,QLineEdit,QStyle
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlQuery,QSqlDatabase
from PyQt6 import uic
from PyQt6.QtGui import QIcon
import importlib_resources

from astrodom.fitsBrowser import FitsBrowser
from astrodom.dashboard import Dashboard
from astrodom.projects import Projects  
from astrodom.logHandler import QTextEditLogger,ColorFormatter  
from astrodom.settings import SettingsDialog  
from astrodom.loadSettings import *  # Import the constants
from astrodom.charts import Charts 
from astrodom.starAnalysis import StarAnalysis
from astrodom.syncProgress import SyncProgress

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Star Analysis file path
        self.starAnalysisFilePath = None
        
        # Load the UI file
        self.rsc_path = importlib_resources.files("astrodom").joinpath('rsc')
        #self.rsc_path = os.path.join(os.path.dirname(__file__), 'rsc')

        uic.loadUi((self.rsc_path.joinpath( 'gui', 'mainWindow.ui')), self)

        # Initialize the log widget at the bottom of the window
        self.logEdit = self.findChild(QTextEdit, 'logEdit')
        self.logEdit.setReadOnly(True)

        # Set up logging
        self.setup_logging()

        # Create the database if it doesn't exist
        self.createDB()

        #Initialize the main window
        self.setWindowTitle("AstroDom 2.0")
        self.setGeometry(100, 100, 800, 600)

        # Integrate the Dashboard widget
        self.dashboard = Dashboard(self)
        dashboard_widget = self.findChild(QWidget, 'dashboard')
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(0, 5, 0, 5)
        dashboard_layout.addWidget(self.dashboard)
        self.dashboard.clicked.connect(self.on_table_row_clicked)

        # Initialize projectsComboBox
        self.projectsComboBox = self.findChild(QComboBox, 'projectsComboBox')

        # Create buttons and icons
        self.newProjectButton = self.findChild(QPushButton, 'newProjectButton')
        self.newProjectButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        
        self.editProjectButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))

        self.syncButton = self.findChild(QPushButton, 'syncButton')
        self.syncButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))

        self.chartsButton = self.findChild(QPushButton, 'chartsButton')
        self.chartsButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'chart-up.png'))))
        self.charts_widget = None

        self.settingsButton = self.findChild(QPushButton, 'settingsButton')
        self.settingsButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'gear.png'))))

        self.starAnalysisButton = self.findChild(QPushButton, 'starAnalysisButton')
        self.starAnalysisButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.fwhmEdit = self.findChild(QLineEdit, 'fwhmEdit')
        self.snrEdit = self.findChild(QLineEdit, 'snrEdit')
        self.altEdit = self.findChild(QLineEdit, 'altEdit')
        self.eccentricityEdit = self.findChild(QLineEdit, 'eccentricityEdit')
        self.setThresholdsButton = self.findChild(QPushButton, 'setThresholdsButton')
        self.setThresholdsButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))

        self.fileOpButton = self.findChild(QPushButton, 'fileOpButton')
        self.fileOpButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))

        # Disable buttons if no project is selected
        self.syncButton.setEnabled(False)
        self.editProjectButton.setEnabled(False)
        self.chartsButton.setEnabled(False)

        # Enable buttons when a project is selected
        self.projectsComboBox.currentIndexChanged.connect(self.update_button_states)

        # Set default values for threshold inputs
        self.fwhmEdit.setText(str(FWHM_LIMIT_DEFAULT))
        self.snrEdit.setText(str(SNR_LIMIT_DEFAULT))
        self.altEdit.setText(str(ALT_LIMIT_DEFAULT))
        self.eccentricityEdit.setText(str(ECCENTRICITY_LIMIT_DEFAULT))

        # Connect the buttons to their respective functions
        self.newProjectButton.clicked.connect(self.open_new_project_dialog)
        self.editProjectButton.clicked.connect(self.open_edit_project_dialog)
        self.syncButton.clicked.connect(self.syncButtonPressed)
        self.chartsButton.clicked.connect(self.open_charts_dialog)
        self.setThresholdsButton.clicked.connect(self.setThresholds)
        self.settingsButton.clicked.connect(self.open_settings_dialog)
        self.starAnalysisButton.clicked.connect(self.open_staranalysis_dialog)
        self.fileOpButton.clicked.connect(self.open_fileOperation_dialog)

        # Populate the projectsComboBox with items from the projects table
        self.projectsComboBox = self.findChild(QComboBox, 'projectsComboBox')
        self.load_projects_combobox()
        self.projectsComboBox.currentIndexChanged.connect(self.update_dashboard_contents)


    def syncButtonPressed(self):
        logging.debug(f"Entering syncButtonPressed for project {self.projectsComboBox.currentData()}")

        # syncButton is a toggle button, if it is checked, the thread is started
        # If it is unchecked, the thread is stopped
        if self.syncButton.text() == 'Stop Sync':
            self.thread.stop()
            self.thread.wait()
            logging.warning("Sync stopped")

            # After the thread is stopped, the buttons are re-enabled
            self.chartsButton.setEnabled(True)
            self.syncButton.setText('Sync Folder')
            self.projectsComboBox.setEnabled(True)
            self.editProjectButton.setEnabled(True)
            self.newProjectButton.setEnabled(True)
            self.settingsButton.setEnabled(True)
            self.setThresholdsButton.setEnabled(True)
            self.fileOpButton.setEnabled(True)
            # and the function returns
            return
        
        # If the button is checked, the thread is started
        # The project ID is retrieved from the projectsComboBox
        current_data = self.projectsComboBox.currentData()
        if current_data is not None:
            selected_project_id = int(current_data)
            query = QSqlQuery()
            query.prepare("SELECT BASE_DIR FROM projects WHERE ID = :id")
            query.bindValue(":id", selected_project_id)
            
            if query.exec() and query.next():
                base_dir = query.value(0)
  
            #Check if images are already in the database for this project
            bResync = True                          
            query.prepare("SELECT COUNT(*) FROM images WHERE PROJECT_ID = :id")
            query.bindValue(":id", selected_project_id)
            if query.exec() and query.next():    
                if query.value(0) > 0:
                    reply = QMessageBox.question(self, 'Sync Folder', 
                    '''This project already contains images in the database. \n
                    YES - Read again all the files from the base folder and delete records in the database for this project\n 
                    NO - Only new files will be inserted in the database and files not in the filesystem will be removed from the database \n 
                    If you want to update values like  FWHM, SNR, etc.), you have to resync (YES).''', 
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    
                    if reply == QMessageBox.StandardButton.No:
                        logging.info("Resync not selected")
                        bResync = False
                    

            # The FitsBrowser thread is created and started 
            # Two signals are connected to the thread: one for logging and one for updating the dashboard
            # when the thread is completed.
            self.thread = FitsBrowser(project_id=selected_project_id, base_dir=base_dir, bResync=bResync,parent=self)
            self.thread.taskCompleted.connect(self.dashboard.load_data)
            self.thread.threadLogger.connect(lambda message,logType: self.threadLogger(message,logType))

            self.thread.start()
            # Open the sync progress dialog

            self.sync_progress_dialog = SyncProgress(self.thread, self)
            self.sync_progress_dialog.show()
            # During file parsing, all widget that could have conflict are disabled
            # Then renabled after thread completion 
            if self.thread.isRunning():
                logging.debug("Sync is running")
                self.chartsButton.setEnabled(False)
                self.syncButton.setText('Stop Sync')
                self.projectsComboBox.setEnabled(False)
                self.editProjectButton.setEnabled(False)
                self.newProjectButton.setEnabled(False)
                self.settingsButton.setEnabled(False)
                self.setThresholdsButton.setEnabled(False)
                self.fileOpButton.setEnabled(False)

                self.thread.taskCompleted.connect(self.on_task_completed)

        return
    
    def on_task_completed(self):
        # When the thread is completed, the buttons are re-enabled
        self.chartsButton.setEnabled(True)
        self.projectsComboBox.setEnabled(True)
        self.editProjectButton.setEnabled(True)
        self.newProjectButton.setEnabled(True)
        self.settingsButton.setEnabled(True)
        self.setThresholdsButton.setEnabled(True)
        self.fileOpButton.setEnabled(True)
        self.syncButton.setText('Sync Folder')

        logging.debug("Sync completed")

    # Set up logging handler
    # This handler will redirect all log messages to the logEdit widget no file logging
    # In a thread use signals to send the log message to the main thread and then to the log widget
    def setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(level=LOGGING_LEVEL)
        qt_handler = QTextEditLogger(self.logEdit)
        qt_handler.setFormatter(ColorFormatter(' %(levelname)s - %(message)s'))
        logger.addHandler(qt_handler)
        
        if FILE_LOG == "YES":
            # Add file logging
            file_handler = logging.FileHandler('astrodom.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)

    # Function to log messages emitted from a thread
    # Example of how to use this function in a thread:     
    # threadLogger = pyqtSignal(str,str)
    # self.threadLogger.emit(message,logType)
    def threadLogger(self, message="", logType="info"):
        if logType == "info":
            logging.info(message)
        elif logType == "debug":
            logging.debug(message)
        elif logType == "warning":
            logging.warning(message)
        elif logType == "error":
            logging.error(message)
        elif logType == "critical":
            logging.critical(message)
        else: 
            logging.info(message)

    # Some actions are only available when a project is selected
    def update_button_states(self):
        current_data = self.projectsComboBox.currentData()
        is_project_selected = current_data is not None and current_data != 0
        self.syncButton.setEnabled(is_project_selected)
        self.editProjectButton.setEnabled(is_project_selected)
        self.chartsButton.setEnabled(is_project_selected)
        self.starAnalysisButton.setEnabled(is_project_selected)
        self.fileOpButton.setEnabled(is_project_selected)
    
    # Update the dashboard contents when a project is selected
    # This function is connected to the projectsComboBox currentIndexChanged signal
    def update_dashboard_contents(self):
        current_data = self.projectsComboBox.currentData()
        if current_data is not None:
            selected_project_id = int(current_data)

            # Disable the sync button if the project is not active
            # not active projects are unlinked from the file system
            # so syncing is not possible 'type': 'filter',

            query = QSqlQuery()
            query.prepare("SELECT NAME,STATUS, DATE,BASE_DIR  FROM projects WHERE ID = :id")
            query.bindValue(":id", selected_project_id)
            if query.exec() and query.next():
                self.projectStatus = query.value(1)
                if self.projectStatus != 'Active':
                    self.syncButton.setEnabled(False)
                else:
                    self.syncButton.setEnabled(True)
                logging.info(f"Selected project: {query.value(0)} ({query.value(2)},{query.value(1)})")
                logging.info(f"Project base folder: {query.value(3)} ")
                self.dashboard.setProjectID(selected_project_id)

    # Handle the threshold values set by the user
    # and calls the applyThreshold method of the dashboard widget
    def setThresholds(self):
        fwhm = self.fwhmEdit.text()
        snr = self.snrEdit.text()
        alt = self.altEdit.text()
        eccentricity = self.eccentricityEdit.text()

        self.dashboard.applyThreshold(fwhm, snr, alt, eccentricity)
    
    # Open the settings dialog
    def open_settings_dialog(self):
        logging.info("Opening settings dialog")
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
    
    # Open the star analysis dialog
    def open_staranalysis_dialog(self):
        logging.info("Opening star analysis dialog")

        if self.starAnalysisFilePath is not None and self.starAnalysisFilePath != "":
            if os.path.exists(self.starAnalysisFilePath):
                logging.info(f"Selected image: {self.starAnalysisFilePath}")
                self.starAnalysis = StarAnalysis(self,self.starAnalysisFilePath)
                self.starAnalysis.show()
            else:
             logging.warning(f"Selected image file does not exist: {self.starAnalysisFilePath}")
        else:
            logging.warning("No valid image file selected")

    # Handle the click event on he table row and gets the file path that
    # Star Analysis will use to analyze the image
    def on_table_row_clicked(self, index):

        source_index = self.dashboard.proxy_model.mapToSource(index)
        source_model = self.dashboard.proxy_model.sourceModel()
        source_index = source_index.siblingAtColumn(21)
    
        self.starAnalysisFilePath = source_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        
        return
    
    # Open the file operationsdialog
    def open_fileOperation_dialog(self):
        logging.info("Opening open_fileOperation_dialog")
        reply = QMessageBox.question(self, 'File operations', 
                                     'The File operations tool is not yet ready.', 
                                     QMessageBox.StandardButton.Ok)
        
        return
    
    # Open the charts dialog
    def open_charts_dialog(self):
        logging.info("Opening charts dialog")
        charts_widget = Charts(self.dashboard.df, self)
        charts_widget.exec()
    
    # Open the projects dialog
    def open_new_project_dialog(self):
        dialog = Projects(self)
        dialog.project_updated.connect(self.load_projects_combobox)
        dialog.exec()

    # Open the projects dialog with the selected project
    def open_edit_project_dialog(self):
        current_project_id = self.projectsComboBox.currentData()

        dialog = Projects(self, project_id=current_project_id)
        dialog.project_updated.connect(self.load_projects_combobox)
        dialog.exec()

    # Load the projects into the projectsComboBox
    def load_projects_combobox(self, project_id=None):
        self.projectsComboBox.clear()
        selected_project_id = project_id

        query = QSqlQuery("SELECT NAME,ID, DATE, STATUS FROM projects ORDER BY CASE STATUS WHEN 'Active' THEN 1 WHEN 'Completed' THEN 2 WHEN 'Archived' THEN 3 END, DATE DESC")
        
        self.projectsComboBox.addItem('---------- Select project ----------', 0)

        while query.next():
            project_name = f"{query.value(0)} ({query.value(2)}, {query.value(3)})"
            project_id = query.value(1)
            self.projectsComboBox.addItem(project_name,project_id)
        
        if selected_project_id and selected_project_id > 0:
            index = self.projectsComboBox.findData(selected_project_id)
            if index != -1:
                self.projectsComboBox.setCurrentIndex(index)

    # AstroDom uses a SQLite database to store project and image data
    # This function creates the database if it doesn't exist
    # The DBNAME constant is defined in the Settings and stored in 
    # settings.json file
    def createDB(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        
        db_path = str(self.rsc_path.joinpath( DBNAME))
        db_exists = os.path.exists(db_path)
        logging.info(f"Database path: {db_path}")
        
        self.db.setDatabaseName(db_path)
        if self.db.open():
            if not db_exists:

                try:
                    query = QSqlQuery()
                    query.exec(
                        """
                        CREATE TABLE IF NOT EXISTS images (
                        PROJECT_ID INTEGER,
                        OBJECT VARCHAR(255),
                        DATE_OBS VARCHAR(255),
                        FILTER VARCHAR(255),
                        EXPOSURE INTEGER,
                        CCD_TEMP REAL,
                        IMAGETYP VARCHAR(255),
                        XBINNING INTEGER,
                        OBJECT_RA VARCHAR(255),
                        OBJECT_DEC VARCHAR(255),
                        OBJECT_ALT VARCHAR(255),
                        OBJECT_AZ VARCHAR(255),
                        GAIN INTEGER,
                        OFFSET INTEGER,
                        FWHM REAL,
                        ECCENTRICITY REAL,
                        FILE VARCHAR(255) UNIQUE,
                        SIZE INTEGER,
                        MEAN REAL,
                        MEDIAN REAL,
                        STD REAL,
                        FOREIGN KEY(PROJECT_ID) REFERENCES projects(ID)
                        )
                        """
                    )
                    query.exec(
                        """
                        CREATE TABLE IF NOT EXISTS projects (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        NAME VARCHAR(255),
                        DATE VARCHAR(255),
                        BASE_DIR VARCHAR(255),
                        STATUS VARCHAR(255) DEFAULT 'Active'
                        )
                        """
                    )
                    query.exec("CREATE INDEX idx_file ON images (FILE)")
                    query.exec("CREATE INDEX idx_project_id ON images (PROJECT_ID)")
                    
                    logging.info(f"{DBNAME} created successfully")

                except Exception as e:
                    logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())