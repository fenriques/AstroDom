import os, sys, logging

from PyQt6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QWidget,QPushButton,QComboBox,QTextEdit,QLineEdit,QStyle
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtSql import QSqlQuery,QSqlDatabase
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import importlib_resources
from astrodom.charts import Charts 
from astrodom.dashboard import Dashboard
from astrodom.fitsBrowser import FitsBrowser
from astrodom.loadSettings import *  # Import the constants
from astrodom.logHandler import QTextEditLogger,ColorFormatter  
from astrodom.projects import Projects  
from astrodom.settings import SettingsDialog  
from astrodom.starAnalysis import StarAnalysis
from astrodom.syncProgress import SyncProgress
from astrodom.fileOperation import FileOperationDialog
from astrodom.previewAndDataWidget import PreviewAndDataWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Star Analysis file path
        self.fileAtSelectedRow = None
        
        # Load the UI file
        self.rsc_path = importlib_resources.files("astrodom").joinpath('rsc')

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

        # Initialize PreviewAndDataWidget
        previewAndDataWidget = self.findChild(QWidget, 'PreviewAndDataWidget')
        if previewAndDataWidget:
            self.previewAndDataWidget = PreviewAndDataWidget(self)
            fits_header_layout = QVBoxLayout(previewAndDataWidget)
            fits_header_layout.setContentsMargins(0, 5, 0, 5)
            fits_header_layout.addWidget(self.previewAndDataWidget)
        else:
            logging.error("PreviewAndDataWidget not found")

        # Initialize projectsComboBox
        self.projectsComboBox = self.findChild(QComboBox, 'projectsComboBox')
        self.load_projects_combobox()
        self.projectsComboBox.currentIndexChanged.connect(self.update_dashboard_contents)

        # New Peoject 
        self.newProjectButton = self.findChild(QPushButton, 'newProjectButton')
        self.newProjectButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        self.newProjectButton.clicked.connect(self.open_new_project_dialog)

        # Edit Project
        self.editProjectButton = self.findChild(QPushButton, 'editProjectButton')
        self.editProjectButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.editProjectButton.clicked.connect(self.open_edit_project_dialog)

        # Sync Button
        self.syncButton = self.findChild(QPushButton, 'syncButton')
        self.syncButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.syncButton.clicked.connect(self.syncButtonPressed)

        # Charts Button
        self.chartsButton = self.findChild(QPushButton, 'chartsButton')
        self.chartsButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'chart-up.png'))))
        self.charts_widget = None
        self.chartsButton.clicked.connect(self.open_charts_dialog)

        # Settings Button
        self.settingsButton = self.findChild(QPushButton, 'settingsButton')
        self.settingsButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'gear.png'))))
        self.settingsButton.clicked.connect(self.open_settings_dialog)

        # Star Analysis Button
        self.starAnalysisButton = self.findChild(QPushButton, 'starAnalysisButton')
        self.starAnalysisButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.starAnalysisButton.clicked.connect(self.open_staranalysis_dialog)
        self.starAnalysisButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'star.png'))))

        # Archive Button
        self.projectsArchiveButton = self.findChild(QPushButton, 'projectsArchiveButton')
        self.projectsArchiveButton.setCheckable(True)
        self.projectsArchiveButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.projectsArchiveButton.clicked.connect(self.toggle_projectsArchive)
        self.projectsArchiveButton.setIcon(QIcon(str(self.rsc_path.joinpath( 'icons', 'keyword.png'))))

        # File Operations Button
        self.fileOpButton = self.findChild(QPushButton, 'fileOpButton')
        self.fileOpButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.fileOpButton.clicked.connect(self.open_fileOperation_dialog)

        # Thresholds
        self.fwhmEdit = self.findChild(QLineEdit, 'fwhmEdit')
        self.fwhmEdit.setText(str(FWHM_LIMIT_DEFAULT))
        self.snrEdit = self.findChild(QLineEdit, 'snrEdit')
        self.snrEdit.setText(str(SNR_LIMIT_DEFAULT))
        self.altEdit = self.findChild(QLineEdit, 'altEdit')
        self.altEdit.setText(str(ALT_LIMIT_DEFAULT))
        self.eccentricityEdit = self.findChild(QLineEdit, 'eccentricityEdit')
        self.eccentricityEdit.setText(str(ECCENTRICITY_LIMIT_DEFAULT))

        self.setThresholdsButton = self.findChild(QPushButton, 'setThresholdsButton')
        self.setThresholdsButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.setThresholdsButton.clicked.connect(self.setThresholds)
        
        self.filterSelectComboBox = self.findChild(QComboBox, 'filterSelectComboBox')
        self.filterSelectComboBox.addItems(["--Filter--", "L", "R", "G", "B", "Ha", "Oiii", "Sii"])
        self.filterSelectComboBox.currentIndexChanged.connect(self.filter_dashboard)
        
        # Target items are loaded when a project is selected in load_projects_combobox
        self.targetComboBox = self.findChild(QComboBox, 'targetComboBox')
        self.targetComboBox.currentIndexChanged.connect(self.filter_dashboard)


    # Called when the sync button is pressed, this function starts the FitsBrowser thread
    # The thread is started with the project ID and the base folder
    # The thread is connected to the dashboard widget to update the data
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
YES, FULL RESYNC: Read again all the files from the base folder for this project\n 
NO, ONLY DIFF: Only new files will be inserted in the database and files not in the filesystem anymore will be removed from the database \n 
Examples: If you want to update values like  FWHM, SNR, etc.), you have to resync (YES). If you just add files from a new imaging session, you can select NO. \n''', 
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

                    if reply == QMessageBox.StandardButton.Cancel:
                        logging.info("Sync operation cancelled")
                        return
                    
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
    
    # When the sync thread is completed, the buttons are re-enabled
    def on_task_completed(self):
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

    # Load the projects into the projectsComboBox
    def load_projects_combobox(self, project_id=None,status="Active"):
        self.projectsComboBox.clear()
        selected_project_id = project_id
        logging.info(f"Selected project id: {selected_project_id}")

        query = QSqlQuery(f"SELECT NAME,ID, DATE, STATUS FROM projects WHERE STATUS = '{status}' ORDER BY DATE DESC")
        logging.info(f"SELECT NAME,ID, DATE, STATUS FROM projects WHERE STATUS = '{status}' ORDER BY DATE DESC")
        # Important: decided to force the user to select a project
        # so the first item in the combobox is selected by default
        #self.projectsComboBox.addItem('---------- Select project ----------', 0)

        while query.next():
            project_name = f"{query.value(0)} ({query.value(2)}, {query.value(3)})"
            project_id = query.value(1)
            self.projectsComboBox.addItem(project_name,project_id)
        
        if selected_project_id and selected_project_id > 0:
            index = self.projectsComboBox.findData(selected_project_id)
            if index != -1:
                self.projectsComboBox.setCurrentIndex(index)
        
        # This is need to load a default project in the dashboard.
        self.update_dashboard_contents()
        self.loadTargetComboBox()

    # Load the targets into the targetComboBox
    def loadTargetComboBox(self):
        self.targetComboBox.clear()
        self.targetComboBox.addItems(["--Target--"])
        project_id = self.projectsComboBox.currentData()


        query = QSqlQuery()
        query.prepare("SELECT DISTINCT OBJECT FROM images WHERE PROJECT_ID = :id")
        query.bindValue(":id", project_id)
        query.exec()

        while query.next():
            target = query.value(0)
            self.targetComboBox.addItem(target)
            logging.info(f"Target: {target}")

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
                
                # Reset the filter combobox
                self.filterSelectComboBox.setCurrentIndex(0)
                # Reset the target loading the new targets for the selected project
                self.loadTargetComboBox()

    # Handle the threshold values set by the user
    # and calls the applyThreshold method of the dashboard widget
    def setThresholds(self):
        fwhm = self.fwhmEdit.text()
        snr = self.snrEdit.text()
        alt = self.altEdit.text()
        eccentricity = self.eccentricityEdit.text()

        self.dashboard.applyThreshold(fwhm, snr, alt, eccentricity,)

    # Filter the dashboard
    def filter_dashboard(self):
        self.dashboard.load_data()

        return    
        
    # Open the settings dialog
    def open_settings_dialog(self):
        logging.info("Opening settings dialog")
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()

    # Open the archive dialog
    def toggle_projectsArchive(self):
        logging.info("Opening projects archive")

        if self.projectsArchiveButton.isChecked():
            self.load_projects_combobox(status = "Archived")
            self.newProjectButton.setEnabled(False)
            self.editProjectButton.setEnabled(False)
            self.syncButton.setEnabled(False)
            self.starAnalysisButton.setEnabled(False)
            self.fileOpButton.setEnabled(False)
            self.previewAndDataWidget.setVisible(False)
        else:
            self.load_projects_combobox(status = "Active")
            self.newProjectButton.setEnabled(True)
            self.editProjectButton.setEnabled(True)
            self.syncButton.setEnabled(True)
            self.starAnalysisButton.setEnabled(True)
            self.fileOpButton.setEnabled(True)
            self.previewAndDataWidget.setVisible(True)

    # Open the star analysis dialog
    def open_staranalysis_dialog(self):
        logging.info("Opening star analysis dialog")

        if self.fileAtSelectedRow is not None and self.fileAtSelectedRow != "":
            if os.path.exists(self.fileAtSelectedRow):
                logging.info(f"Selected image: {self.fileAtSelectedRow}")
                self.starAnalysis = StarAnalysis(self,self.fileAtSelectedRow)
                self.starAnalysis.show()
            else:
             logging.warning(f"Selected image file does not exist: {self.fileAtSelectedRow}")
        else:

            fits_path, _ = QFileDialog.getOpenFileName(self, "Select a FITS File", "", "FITS Files (*.fits *.fit *.FITS *.FIT)")
            if not fits_path or not fits_path.lower().endswith(('.fits', '.fit')):
                QMessageBox.warning(self, "Invalid File", "The selected file is not a valid FITS file.")
                return
            else:    
                self.starAnalysis = StarAnalysis(self, fits_path)
                self.starAnalysis.show()

    # Handle the click event on he table row and gets the file path that
    # Star Analysis will use to analyze the image
    def on_table_row_clicked(self, index):

        #If a Target grouping row or a Filter grouping row is clicked there is no file to analyze
        if not index.parent().isValid() or not index.parent().parent().isValid():
            return
        
        source_index = self.dashboard.proxy_model.mapToSource(index)
        source_model = self.dashboard.proxy_model.sourceModel()
        source_index = source_index.siblingAtColumn(25)
    
        self.fileAtSelectedRow = source_model.data(source_index, Qt.ItemDataRole.DisplayRole)
        self.itemsAtSelectedRow = [source_model.data(source_index.siblingAtColumn(col), Qt.ItemDataRole.DisplayRole) for col in range(source_model.columnCount())]
        self.previewAndDataWidget.setItemsAtSelectedRow(self.itemsAtSelectedRow)
  
        return

    # Open the file operationsdialog
    def open_fileOperation_dialog(self):
        logging.info("Opening open_fileOperation_dialog")
        checked_files = self.dashboard.proxy_model.sourceModel().get_checked_files()
        if len(checked_files) == 0:
            QMessageBox.warning(self, 'No Files Selected', 'File operations are not possible if no images are selected.', QMessageBox.StandardButton.Ok)
            return
        fileOperationDialog = FileOperationDialog(checked_files,self)
        #fileOperationDialog.filesDeleted.connect(self.refresh_dashboard_model)  

        fileOperationDialog.exec()
        
    
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
                        SITELAT VARCHAR(255),
                        SITELONG VARCHAR(255),
                        MOON_PHASE REAL,
                        MOON_SEPARATION REAL,
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