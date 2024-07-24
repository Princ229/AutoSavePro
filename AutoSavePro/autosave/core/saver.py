import os
import shutil
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Saver:
    def __init__(self, base_save_directory):
        self.base_save_directory = base_save_directory
        logging.info(f"Saver initialized with base save directory: {base_save_directory}")

    def create_save_directory(self, app_name):
        save_dir = os.path.join(self.base_save_directory, app_name)
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
                logging.info(f"Created save directory: {save_dir}")
            except Exception as e:
                logging.error(f"Failed to create save directory {save_dir}: {str(e)}")
                return None
        return save_dir

    def save_file(self, file_path, app_name):
        save_dir = self.create_save_directory(app_name)
        if not save_dir:
            return None

        file_name = os.path.basename(file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
        save_path = os.path.join(save_dir, save_name)

        try:
            shutil.copy2(file_path, save_path)
            logging.info(f"File saved: {save_path}")
            return save_path
        except Exception as e:
            logging.error(f"Error saving file {file_path}: {str(e)}")
            return None

    def restore_file(self, save_path, original_path):
        try:
            shutil.copy2(save_path, original_path)
            logging.info(f"File restored: {original_path}")
            return True
        except Exception as e:
            logging.error(f"Error restoring file {save_path}: {str(e)}")
            return False

    def list_saves(self, app_name, file_name):
        save_dir = os.path.join(self.base_save_directory, app_name)
        if not os.path.exists(save_dir):
            logging.warning(f"Save directory does not exist: {save_dir}")
            return []

        saves = []
        for file in os.listdir(save_dir):
            if file.startswith(os.path.splitext(file_name)[0]) and file.endswith(os.path.splitext(file_name)[1]):
                saves.append(os.path.join(save_dir, file))
        logging.info(f"Found {len(saves)} saves for {file_name} in {app_name}")
        return sorted(saves, key=os.path.getmtime, reverse=True)

    def delete_old_saves(self, app_name, file_name, keep_count=5):
        saves = self.list_saves(app_name, file_name)
        if len(saves) > keep_count:
            for old_save in saves[keep_count:]:
                try:
                    os.remove(old_save)
                    logging.info(f"Deleted old save: {old_save}")
                except Exception as e:
                    logging.error(f"Error deleting old save {old_save}: {str(e)}")

if __name__ == "__main__":
    # Example usage
    saver = Saver("C:/AutoSavePro/Saves")
    
    # Save a file
    saved_path = saver.save_file("C:/Users/YourUsername/Documents/test.txt", "BlocNotes")
    if saved_path:
        logging.info(f"File saved successfully: {saved_path}")
    else:
        logging.error("Failed to save file")
    
    # List saves for a file
    saves = saver.list_saves("BlocNotes", "test.txt")
    for save in saves:
        logging.info(f"Found save: {save}")
    
    # Restore the most recent save
    if saves:
        if saver.restore_file(saves[0], "C:/Users/YourUsername/Documents/test.txt"):
            logging.info("File restored successfully")
        else:
            logging.error("Failed to restore file")
    else:
        logging.warning("No saves found to restore")
    
    # Delete old saves
    saver.delete_old_saves("BlocNotes", "test.txt", keep_count=5)