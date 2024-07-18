# main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from autosave.gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting AutoSavePro application")
    
    app = QApplication(sys.argv)
    
    # Créer la fenêtre principale
    mainWin = MainWindow()
    
    # Créer et configurer le watcher
    base_save_directory = "C:/AutoSavePro/Saves"
    watcher = mainWin.watcher_thread.watcher
    watcher.add_application("notepad.exe", [".txt"])
    
    # Connecter le watcher à la fenêtre principale
    watcher.log_signal.connect(mainWin.update_log)
    
    # Afficher la fenêtre principale
    mainWin.show()
    logging.info("AutoSavePro GUI initialized and shown")
    
    # Démarrer le thread du watcher
    mainWin.watcher_thread.start()
    logging.info("Watcher thread started")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
