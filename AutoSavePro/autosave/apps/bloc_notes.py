import os
import subprocess
import time
import logging
import win32gui
import win32process
import psutil
import threading
from queue import Queue

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BlocNotesHandler:
    def __init__(self):
        self.notepad_windows = []
        logging.info("BlocNotesHandler initialized")

    def find_notepad_windows(self):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and 'Bloc-notes' in win32gui.GetWindowText(hwnd):
                hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        self.notepad_windows = hwnds
        logging.info(f"Found {len(self.notepad_windows)} Bloc-notes windows")
        for hwnd in hwnds:
            logging.debug(f"Window handle: {hwnd}, Title: {win32gui.GetWindowText(hwnd)}")
        return self.notepad_windows

    def get_open_files(self):
        open_files = []
        for hwnd in self.notepad_windows:
            window_title = win32gui.GetWindowText(hwnd)
            logging.debug(f"Checking window title: {window_title}")
            if ' - Bloc-notes' in window_title:
                file_name = window_title.split(' - ')[0].strip()
                logging.debug(f"Extracted file name: {file_name}")
                possible_paths = [
                    os.path.join(os.path.expanduser('~'), 'Desktop', file_name),
                    os.path.join(os.path.expanduser('~'), 'Documents', file_name)
                ]
                for path in possible_paths:
                    logging.debug(f"Checking path: {path}")
                    if os.path.isfile(path):
                        open_files.append(path)
                        logging.info(f"Found open file: {path}")
                        break
                else:
                    logging.warning(f"File path extracted from window title is not valid: {file_name}")
        logging.info(f"Found {len(open_files)} open files in Bloc-notes")
        return open_files

    def save_document(self, file_path):
        try:
            logging.info(f"Attempting to save document: {file_path}")
            subprocess.run(['powershell', '-command', '(New-Object -ComObject WScript.Shell).SendKeys("^s")'], check=True, timeout=5)
            time.sleep(0.5)
            logging.info(f"Successfully sent save command for: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving Bloc-notes document {file_path}: {str(e)}")
            return False

    def is_notepad_running(self):
        for proc in psutil.process_iter(['name']):
            if 'notepad.exe' in proc.info['name'].lower():
                logging.info("Notepad.exe is running")
                return True
        logging.info("Notepad.exe is not running")
        return False

def autosave_worker(save_directory, result_queue):
    handler = BlocNotesHandler()
    if handler.is_notepad_running():
        handler.find_notepad_windows()
        open_files = handler.get_open_files()
        for file in open_files:
            if handler.save_document(file):
                base_name = os.path.basename(file)
                save_path = os.path.join(save_directory, f"AutoSave_{base_name}")
                try:
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(file, 'rb') as src, open(save_path, 'wb') as dst:
                        dst.write(src.read())
                    logging.info(f"Autosaved Bloc-notes document: {save_path}")
                    result_queue.put(("success", f"Autosaved: {save_path}"))
                except Exception as e:
                    logging.error(f"Failed to save autosaved file: {str(e)}")
                    result_queue.put(("error", f"Failed to save: {file}"))
            else:
                logging.error(f"Failed to autosave Bloc-notes document: {file}")
                result_queue.put(("error", f"Failed to save: {file}"))
    else:
        logging.info("Notepad is not running, no autosave performed")
        result_queue.put(("info", "Notepad is not running"))

def autosave_bloc_notes(save_directory):
    result_queue = Queue()
    thread = threading.Thread(target=autosave_worker, args=(save_directory, result_queue))
    thread.start()
    thread.join(timeout=30)  # Wait for up to 30 seconds

    if thread.is_alive():
        logging.error("Autosave operation timed out")
        return "Autosave operation timed out"

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results

if __name__ == "__main__":
    # Example usage
    save_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'AutoSavePro', 'Saves', 'BlocNotes')
    results = autosave_bloc_notes(save_dir)
    print("Autosave results:", results)
