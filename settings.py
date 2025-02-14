import sys,json,logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFrame, QComboBox, QApplication

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 300)

        # Load settings from JSON file
        self.settings = self.load_settings()

        # Create layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # Create line edits for each setting
        self.dbname_edit = QLineEdit(self.settings.get("DBNAME", "").rstrip('.db'))
        self.alt_limit_edit = QLineEdit(str(self.settings.get("ALT_LIMIT_DEFAULT", 0)))
        self.fwhm_limit_edit = QLineEdit(str(self.settings.get("FWHM_LIMIT_DEFAULT", 0)))
        self.eccentricity_limit_edit = QLineEdit(str(self.settings.get("ECCENTRICITY_LIMIT_DEFAULT", 0)))
        self.snr_limit_edit = QLineEdit(str(self.settings.get("SNR_LIMIT_DEFAULT", 0)))

        self.compact_dashboard_edit = QComboBox()
        self.compact_dashboard_edit.addItems(["Compact", "Extended"])
        self.compact_dashboard_edit.setCurrentText(str(self.settings.get("COMPACT_DASHBOARD", "Extended")))

        # Create a combo box for logging levels
        self.logging_level_edit = QComboBox()
        self.logging_level_edit.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.logging_level_edit.setCurrentText(self.settings.get("DATE_FORMAT", "INFO"))

        # Create a combo box for logging levels
        self.file_log = QComboBox()
        self.file_log.addItems(["YES", "NO"])
        self.file_log.setCurrentText(self.settings.get("FILE_LOG", "NO"))

        # Create a combo box for logging levels
        self.date_format_edit = QComboBox()
        self.date_format_edit.addItems(["%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"])
        self.date_format_edit.setCurrentText(self.settings.get("LOGGING_LEVEL", "%Y-%m-%d"))

        form_layout.addRow("Database Name:", self.dbname_edit)
        form_layout.addRow("Logging Level:", self.logging_level_edit)
        form_layout.addRow("Enable Log File :", self.file_log)
        form_layout.addRow(separator)
        form_layout.addRow("Date Format:", self.date_format_edit)
        form_layout.addRow("Dashboard View:", self.compact_dashboard_edit)
        form_layout.addRow(separator)
        form_layout.addRow("ALT Threshold Default:", self.alt_limit_edit)
        form_layout.addRow("FWHM Threshold Default:", self.fwhm_limit_edit)
        form_layout.addRow("Eccentricity Threshold Default:", self.eccentricity_limit_edit)
        form_layout.addRow("SNR Threshold Default:", self.snr_limit_edit)

        # Create save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)

        # Add form layout and save button to main layout
        layout.addLayout(form_layout)
        layout.addWidget(save_button)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error("settings.json file not found.")
            return {}

    def save_settings(self):
        self.settings["DBNAME"] = self.dbname_edit.text() + '.db'
        self.settings["LOGGING_LEVEL"] = self.logging_level_edit.currentText()
        self.settings["FILE_LOG"] = self.file_log.currentText()
        self.settings["DATE_FORMAT"] = self.date_format_edit.currentText()
        self.settings["ALT_LIMIT_DEFAULT"] = float(self.alt_limit_edit.text())
        self.settings["FWHM_LIMIT_DEFAULT"] = float(self.fwhm_limit_edit.text())
        self.settings["ECCENTRICITY_LIMIT_DEFAULT"] = float(self.eccentricity_limit_edit.text())
        self.settings["SNR_LIMIT_DEFAULT"] = float(self.snr_limit_edit.text())
        self.settings["COMPACT_DASHBOARD"] = self.compact_dashboard_edit.currentText()

        if not self.dbname_edit.text():
            logging.error("Database name cannot be empty.")
            return
        if not self.settings["ALT_LIMIT_DEFAULT"]:
            self.settings["ALT_LIMIT_DEFAULT"] = 0.0
        if not self.settings["FWHM_LIMIT_DEFAULT"]:
            self.settings["FWHM_LIMIT_DEFAULT"] = 0.0
        if not self.settings["ECCENTRICITY_LIMIT_DEFAULT"]:
            self.settings["ECCENTRICITY_LIMIT_DEFAULT"] = 0.0
        if not self.settings["SNR_LIMIT_DEFAULT"]:
            self.settings["SNR_LIMIT_DEFAULT"] = 0.0

        with open('settings.json', 'w') as file:
            json.dump(self.settings, file, indent=4)

            logging.debug(f"Settings to be saved: {self.settings}")

        logging.info( "Settings saved successfully.")
        logging.warning( "Please restart AstroDom to reload settings.")
        self.accept()

# Example usage
if __name__ == "__main__":

    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()