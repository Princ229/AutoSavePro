import os
import subprocess
import time
import logging

# Définissez le chemin correct vers l'exécutable GIMP
GIMP_PATH = r"C:\Program Files\GIMP 2\bin\gimp-2.10.exe"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class GIMPHandler:
    def __init__(self):
        self.process = None

    def connect(self):
        try:
            logging.info(f"Attempting to connect to GIMP at: {GIMP_PATH}")
            self.process = subprocess.Popen([GIMP_PATH, '-i', '-b', '(gimp-message "Connected")'], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE)
            time.sleep(2)  # Attendez que GIMP démarre
            stdout, stderr = self.process.communicate()
            logging.debug(f"GIMP stdout: {stdout.decode()}")
            logging.debug(f"GIMP stderr: {stderr.decode()}")
            if "Connected" in stdout.decode():
                logging.info("Successfully connected to GIMP")
                return True
            else:
                logging.error("Failed to receive connection confirmation from GIMP")
                return False
        except Exception as e:
            logging.error(f"Error connecting to GIMP: {str(e)}")
            logging.error(f"GIMP path used: {GIMP_PATH}")
            return False

    def disconnect(self):
        if self.process:
            self.process.terminate()
            self.process = None
            logging.info("Disconnected from GIMP")

    def get_open_files(self):
        if not self.process:
            logging.warning("GIMP process not connected")
            return []
        try:
            self.process.stdin.write(b'(gimp-image-list)\n')
            self.process.stdin.flush()
            output = self.process.stdout.readline().decode().strip()
            logging.info(f"Raw output from GIMP: {output}")
            # Parsez la sortie pour obtenir les noms de fichiers
            # Ceci est une simplification, vous devrez ajuster en fonction de la sortie réelle
            open_files = [file for file in output.split() if file.endswith(('.xcf', '.png', '.jpg'))]
            logging.info(f"Open files in GIMP: {open_files}")
            return open_files
        except Exception as e:
            logging.error(f"Error getting open files from GIMP: {str(e)}")
            return []

    def save_document(self, file_path, save_path):
        if not self.process:
            logging.warning("GIMP process not connected")
            return False
        try:
            script = f"""
            (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{file_path}" "{file_path}")))
                   (drawable (car (gimp-image-get-active-layer image))))
              (gimp-file-save RUN-NONINTERACTIVE image drawable "{save_path}" "{save_path}")
              (gimp-image-delete image))
            """
            self.process.stdin.write(script.encode())
            self.process.stdin.flush()
            time.sleep(1)  # Attendez que la sauvegarde soit terminée
            logging.info(f"Successfully saved GIMP document: {save_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving GIMP document: {str(e)}")
            return False

def autosave_gimp(save_directory):
    handler = GIMPHandler()
    if handler.connect():
        open_files = handler.get_open_files()
        for file in open_files:
            save_path = os.path.join(save_directory, f"AutoSave_{os.path.basename(file)}")
            if handler.save_document(file, save_path):
                logging.info(f"Autosaved GIMP document: {save_path}")
            else:
                logging.error(f"Failed to autosave GIMP document: {file}")
        handler.disconnect()
    else:
        logging.error("Failed to connect to GIMP")

if __name__ == "__main__":
    # Example usage
    autosave_gimp("C:/AutoSavePro/Saves/GIMP")
