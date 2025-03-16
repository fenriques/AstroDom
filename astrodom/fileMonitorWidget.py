import os
import time
import logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from astrodom.syncImages import SyncImages

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

class FileMonitorThread(QThread):
    file_added = pyqtSignal(str)

    def __init__(self, base_dir, parent=None):
        super().__init__(parent)
        self.base_dir = base_dir
        self.observer = Observer()

    def run(self):
        event_handler = FileMonitorHandler(self.on_file_added)
        self.observer.schedule(event_handler, self.base_dir, recursive=True)
        self.observer.start()
        try:
            while self.observer.is_alive():
                time.sleep(1)
        except Exception as e:
            #logging.error(f"Error in file monitor thread: {e}")
            pass
        finally:
            self.observer.stop()
            self.observer.join()

    def on_file_added(self, file_path):
        #logging.info(f"New file detected: {file_path}")
        self.sync_images_thread = SyncImages(project_id=self.project_id, base_dir=self.base_dir, bResync=False, bAutoSync=True,files_path=[file_path], parent=self)
        self.sync_images_thread.start()
    def stop(self):
        self.observer.stop()

class FileMonitorDialog(QDialog):
    def __init__(self, base_dir,project_id, bResync=False, bAutoSync=True,parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.base_dir = base_dir
        self.setWindowTitle("File Monitor")
        self.setModal(True)
        self.layout = QVBoxLayout(self)
        self.label = QLabel(f"Monitoring folder: {self.base_dir}")
        self.layout.addWidget(self.label)
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.layout.addWidget(self.stop_button)

        self.file_monitor_thread = FileMonitorThread(self.base_dir)
        #self.file_monitor_thread.file_added.connect(self.on_file_added)
        self.file_monitor_thread.start()

    def on_file_added(self, file_path):
        #logging.info(f"New file added: {file_path}")
        file_path = [file_path]
        self.sync_images_thread = SyncImages(project_id=self.project_id, base_dir=self.base_dir, bResync=False, bAutoSync=True,files_path=file_path, parent=self)
        self.sync_images_thread.start()

    def stop_monitoring(self):
        self.file_monitor_thread.stop()
        self.file_monitor_thread.wait()
        self.accept()

    def closeEvent(self, event):
        self.stop_monitoring()
        event.accept()