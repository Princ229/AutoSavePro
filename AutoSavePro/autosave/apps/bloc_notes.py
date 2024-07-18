import os
import subprocess
import time
import logging
import win32gui
import win32process
import psutil
import win32api
import win32con

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BlocNotesHandler:
    def __init__(self):
        self.notepad_processes = []
        logging.info("BlocNotesHandler initialized")

    def find_notepad_windows(self):
        def callback(hwnd, hwnds):
            window_title = win32gui.GetWindowText(hwnd)
            logging.debug(f"Found window: {window_title}")
            if win32gui.IsWindowVisible(hwnd) and ('Bloc-notes' in window_title or 'Notepad' in window_title):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                self.notepad_processes.append(pid)
                logging.info(f"Found Bloc-notes window with PID: {pid}")
            return True

        self.notepad_processes = []
        win32gui.EnumWindows(callback, [])
        logging.info(f"Found {len(self.notepad_processes)} Bloc-notes processes")
        return self.notepad_processes

    def get_open_files(self):
        open_files = []
        for pid in self.notepad_processes:
            try:
                process = psutil.Process(pid)
                for handle in process.open_files():
                    if handle.path.lower().endswith('.txt'):
                        open_files.append(handle.path)
                        logging.info(f"Found open file: {handle.path}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logging.error(f"Error accessing process {pid}: {str(e)}")
        
        if not open_files:
            for hwnd in self.get_window_handles('Edit'):
                length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH) + 1
                buffer = win32gui.PyMakeBuffer(length)
                win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length, buffer)
                text = buffer[:length-1].decode('utf-8')
                if text:
                    open_files.append(text)
                    logging.info(f"Found open file via Edit control: {text}")

        logging.info(f"Found {len(open_files)} open files in Bloc-notes")
        return open_files

    def get_window_handles(self, classname):
        def callback(hwnd, hwnds):
            if win32gui.GetClassName(hwnd) == classname:
                hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds

    def save_document(self, file_path):
        try:
            logging.info(f"Attempting to save document: {file_path}")
            subprocess.run(['powershell', '-command', '(New-Object -ComObject WScript.Shell).SendKeys("^s")'])
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

def autosave_bloc_notes(save_directory):
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
                    os.replace(file, save_path)
                    logging.info(f"Autosaved Bloc-notes document: {save_path}")
                except Exception as e:
                    logging.error(f"Failed to move autosaved file: {str(e)}")
            else:
                logging.error(f"Failed to autosave Bloc-notes document: {file}")
    else:
        logging.info("Notepad is not running, no autosave performed")

if __name__ == "__main__":
    # Example usage
    autosave_bloc_notes("C:/AutoSavePro/Saves/BlocNotes")
