# watcher.py
import os
import time
import psutil
import logging
from autosave.core.saver import Saver
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from autosave.apps.bloc_notes import BlocNotesHandler
from PyQt5.QtCore import QObject, pyqtSignal

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ApplicationWatcher:
    def __init__(self, app_name, file_extensions):
        self.app_name = app_name
        self.file_extensions = file_extensions
        self.is_running = False
        self.watched_files = set()
        self.save_frequency = 300  # Default to 5 minutes
        self.last_save_time = time.time()

    def check_if_running(self):
        for proc in psutil.process_iter(['name']):
            if self.app_name.lower() in proc.info['name'].lower():
                self.is_running = True
                logging.debug("{} is running with process name: {}".format(self.app_name, proc.info['name']))
                return True
        self.is_running = False
        logging.debug("{} is not running".format(self.app_name))
        return False

    def get_open_files(self):
        open_files = set()
        for proc in psutil.process_iter(['name', 'open_files']):
            if self.app_name.lower() in proc.info['name'].lower():
                try:
                    files = proc.open_files()
                    for file in files:
                        if any(file.path.endswith(ext) for ext in self.file_extensions):
                            open_files.add(file.path)
                            logging.debug("Found open file for {}: {}".format(self.app_name, file.path))
                except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                    logging.warning("Unable to access files for {}: {}".format(self.app_name, str(e)))
        logging.debug("Open files for {}: {}".format(self.app_name, open_files))
        return open_files

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

class Watcher(QObject):
    log_signal = pyqtSignal(str)

    def __init__(self, base_save_directory):
        super().__init__()
        self.app_watchers = {}
        self.observer = Observer()
        self.saver = Saver(base_save_directory)
        self.bloc_notes_handler = BlocNotesHandler()
        self.base_save_directory = base_save_directory
        self.log_signal.emit("Watcher initialized with base save directory: {}".format(base_save_directory))

    def add_application(self, app_name, file_extensions):
        self.app_watchers[app_name] = ApplicationWatcher(app_name, file_extensions)
        self.log_signal.emit("Added application to watch: {} with extensions {}".format(app_name, file_extensions))

    def set_save_frequency(self, app_name, seconds):
        if app_name in self.app_watchers:
            self.app_watchers[app_name].save_frequency = seconds
            self.log_signal.emit("Set save frequency for {} to {} seconds".format(app_name, seconds))

    def stop_watching_app(self, app_name):
        if app_name in self.app_watchers:
            watcher = self.app_watchers[app_name]
            for file in watcher.watched_files:
                self.observer.unschedule_all()
            watcher.watched_files.clear()
            self.log_signal.emit("Stopped watching {}".format(app_name))
        else:
            self.log_signal.emit("Application {} not found".format(app_name))        

    def start_watching(self):
        self.log_signal.emit("Starting to watch applications...")
        logging.info("Watcher loop started")
        while True:
            for app_name, watcher in self.app_watchers.items():
                if watcher.check_if_running():
                    current_time = time.time()
                    if current_time - watcher.last_save_time >= watcher.save_frequency:
                        self.save_open_files(app_name)
                        watcher.last_save_time = current_time

                    open_files = watcher.get_open_files()
                    new_files = open_files - watcher.watched_files
                    for file in new_files:
                        self.log_signal.emit("Now watching: {}".format(file))
                        event_handler = FileChangeHandler(self.on_file_changed)
                        self.observer.schedule(event_handler, os.path.dirname(file), recursive=False)
                    watcher.watched_files.update(new_files)
                else:
                    for file in watcher.watched_files:
                        self.log_signal.emit("Stopped watching: {}".format(file))
                        self.observer.unschedule_all()
                    watcher.watched_files.clear()

            # Specific handling for Bloc-notes
            if "notepad.exe" in self.app_watchers:
                if self.bloc_notes_handler.is_notepad_running():
                    self.bloc_notes_handler.find_notepad_windows()
                    open_files = self.bloc_notes_handler.get_open_files()
                    if open_files:
                        self.log_signal.emit("Open files in Bloc-notes: {}".format(open_files))
                        self.app_watchers["notepad.exe"].watched_files.update(open_files)
                    else:
                        self.log_signal.emit("No files open in Bloc-notes")
                else:
                    self.log_signal.emit("Notepad is not running")

            time.sleep(10)  # Check every 10 seconds

    def save_open_files(self, app_name):
        watcher = self.app_watchers[app_name]
        open_files = watcher.get_open_files()
        for file_path in open_files:
            self.on_file_changed(file_path)

    def on_file_changed(self, file_path):
        self.log_signal.emit("File changed: {}".format(file_path))
        for app_name, watcher in self.app_watchers.items():
            if file_path in watcher.watched_files:
                self.log_signal.emit("File belongs to {}".format(app_name))
                if app_name == "notepad.exe" and file_path.lower().endswith('.txt'):
                    save_path = os.path.join(self.base_save_directory, "BlocNotes", "AutoSave_{}".format(os.path.basename(file_path)))
                    if self.bloc_notes_handler.save_document(file_path):
                        try:
                            os.makedirs(os.path.dirname(save_path), exist_ok=True)
                            os.replace(file_path, save_path)
                            self.log_signal.emit("Successfully saved Bloc-notes file to {}".format(save_path))
                        except Exception as e:
                            self.log_signal.emit("Error moving saved file: {}".format(str(e)))
                    else:
                        self.log_signal.emit("Failed to save Bloc-notes file")
                else:
                    if self.saver.save_file(file_path, app_name):
                        self.log_signal.emit("Successfully saved file {} for {}".format(file_path, app_name))
                    else:
                        self.log_signal.emit("Failed to save file {} for {}".format(file_path, app_name))
                break

    def run(self):
        self.observer.start()
        try:
            self.start_watching()
        except KeyboardInterrupt:
            self.log_signal.emit("Watcher stopped by user")
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    watcher = Watcher("C:/AutoSavePro/Saves")
    watcher.add_application("notepad.exe", [".txt"])
    watcher.run()
