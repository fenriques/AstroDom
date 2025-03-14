import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtCore import QThread, pyqtSignal
import threading

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

class FileMonitorThread(QThread):
    file_added = pyqtSignal(str,int,str)
    threadLogger = pyqtSignal(str,str)

    def __init__(self, base_directory, project_id, bResync=False, bAutoSync=True,parent=None):
        super().__init__(parent)
        self.bResync = bResync
        self.bAutoSync = bAutoSync
        self.project_id = project_id    
        self.base_directory = base_directory
        self.observer = Observer()

    def run(self):
        event_handler = FileMonitorHandler(self.on_file_added)
        self.observer.schedule(event_handler, self.base_directory, recursive=True)
        self.observer.start()

        try:
            while self.observer.is_alive():
                time.sleep(1)
        except Exception as e:
            
            self.threadLogger.emit(f"Error in file monitor thread: {e}", "error")

        finally:
            self.observer.stop()
            self.observer.join()

    def on_file_added(self, file_path):
        self.file_added.emit(self.base_directory, self.project_id,file_path)

    def stop(self):
        self.observer.stop()