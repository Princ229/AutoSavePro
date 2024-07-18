import os
import win32com.client
import pythoncom

class PhotoshopHandler:
    def __init__(self):
        self.app = None

    def connect(self):
        try:
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("Photoshop.Application")
            return True
        except Exception as e:
            print(f"Error connecting to Photoshop: {str(e)}")
            return False

    def disconnect(self):
        self.app = None
        pythoncom.CoUninitialize()

    def get_active_document(self):
        if not self.app:
            return None
        try:
            return self.app.ActiveDocument
        except:
            return None

    def save_document(self, doc, path):
        if not doc:
            return False
        try:
            
            save_options = win32com.client.Dispatch("Photoshop.PhotoshopSaveOptions")
            doc.SaveAs(path, save_options, True)
            return True
        except Exception as e:
            print(f"Error saving Photoshop document: {str(e)}")
            return False

    def get_open_files(self):
        if not self.app:
            return []
        try:
            return [doc.FullName for doc in self.app.Documents]
        except:
            return []

def autosave_photoshop(save_directory):
    handler = PhotoshopHandler()
    if handler.connect():
        doc = handler.get_active_document()
        if doc:
            original_path = doc.FullName
            file_name = os.path.basename(original_path)
            save_path = os.path.join(save_directory, f"AutoSave_{file_name}")
            if handler.save_document(doc, save_path):
                print(f"Autosaved Photoshop document: {save_path}")
            else:
                print("Failed to autosave Photoshop document")
        else:
            print("No active Photoshop document found")
        handler.disconnect()
    else:
        print("Failed to connect to Photoshop")

if __name__ == "__main__":
    # Example usage
    autosave_photoshop("C:/AutoSavePro/Saves/Photoshop")