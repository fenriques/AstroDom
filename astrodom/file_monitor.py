import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtCore import QThread, pyqtSignal

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
            logging.error(f"Error in file monitor thread: {e}")
        finally:
            self.observer.stop()
            self.observer.join()

    def on_file_added(self, file_path):
        logging.info(f"New file detected: {file_path}")
        self.file_added.emit(file_path)

    def stop(self):
        self.observer.stop()