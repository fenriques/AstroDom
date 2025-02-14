from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QPushButton
from PyQt6.QtCore import pyqtSlot

class SyncProgress(QDialog):


    def __init__(self, thread, parent=None):
        super(SyncProgress, self).__init__(parent)
        self.thread = thread
        self.initUI()
        self.parent = parent

    def initUI(self):
        self.setWindowTitle('Sync Progress')
        self.setGeometry(100, 100, 400, 200)
        self.layout = QVBoxLayout(self)

        self.progressBar = QProgressBar(self)
        self.layout.addWidget(self.progressBar)

        self.stopButton = QPushButton('Stop Sync', self)
        self.stopButton.clicked.connect(self.stopSync)
        self.layout.addWidget(self.stopButton)

        self.thread.nFileSync.connect(self.updateProgress)
        self.thread.nFileTot.connect(self.setMaxFiles)
        self.thread.taskCompleted.connect(self.closeDialog)

    @pyqtSlot(int)
    def updateProgress(self, value):
        self.progressBar.setValue(value)

    @pyqtSlot(int)
    def setMaxFiles(self, value):
        self.progressBar.setMaximum(value)

    @pyqtSlot()
    def closeDialog(self):
        self.accept()

    def stopSync(self):
        if self.stopButton.text() == 'Stop Sync':
            self.thread.stop()
            self.thread.wait()
            #self.parent.logging.warning("Sync stopped")

            # After the thread is stopped, the buttons are re-enabled
            self.parent.chartsButton.setEnabled(True)
            self.parent.syncButton.setText('Sync Folder')
            self.parent.projectsComboBox.setEnabled(True)
            self.parent.editProjectButton.setEnabled(True)
            self.parent.newProjectButton.setEnabled(True)
            self.parent.settingsButton.setEnabled(True)
            self.parent.setThresholdsButton.setEnabled(True)
            # and the function returns
            self.accept()

            return
        