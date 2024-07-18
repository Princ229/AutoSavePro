# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QListWidget, 
                             QListWidgetItem, QComboBox, QFileDialog, QFrame,
                             QTextEdit)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QSize, QRectF, pyqtSignal, QThread
from autosave.core.watcher import Watcher

class WatcherThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, base_save_directory):
        super().__init__()
        self.watcher = Watcher(base_save_directory)
        self.watcher.log_signal.connect(self.log_signal.emit)

    def run(self):
        self.watcher.run()

class OnOffSwitch(QWidget):
    stateChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.is_on = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(QColor("#4CAF50") if self.is_on else QColor("#D32F2F"))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.setBrush(QBrush(QColor("white")))
        if self.is_on:
            painter.drawEllipse(self.width() - 28, 2, 26, 26)
        else:
            painter.drawEllipse(2, 2, 26, 26)

    def mousePressEvent(self, event):
        self.is_on = not self.is_on
        self.update()
        self.stateChanged.emit(self.is_on)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoSavePro")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2C2C2C; color: white;")

        main_layout = QHBoxLayout()

        # Left panel
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")
        left_panel.setFixedWidth(200)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join("AutoSavePro", "autosave", "icons", "logo.png"))
        logo_label.setPixmap(logo_pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        left_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Menu buttons
        menu_buttons = ["Dashboard", "Applications", "Settings", "About"]
        for button_text in menu_buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    font-size: 16px;
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                }
            """)
            left_layout.addWidget(button)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # Right panel
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setStyleSheet("background-color: #2C2C2C; border-radius: 10px;")

        # Title
        title_label = QLabel("Applications")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        right_layout.addWidget(title_label)

        # Application list
        self.app_list = QListWidget()
        self.app_list.setStyleSheet("""
            QListWidget {
                background-color: #2C2C2C;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #3A3A3A;
                border-radius: 10px;
                margin: 5px 0;
            }
            QListWidget::item:selected {
                background-color: #4A4A4A;
            }
        """)
        self.add_app_item("Bloc-notes", "notepad.png")
        right_layout.addWidget(self.app_list)

        # Add application button
        self.add_app_button = QPushButton("Ajouter une nouvelle application")
        self.add_app_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                padding: 15px;
                font-size: 18px;
                border-radius: 5px;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_app_button.clicked.connect(self.add_new_application)
        right_layout.addWidget(self.add_app_button)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: none;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self.log_display)

        main_layout.addWidget(right_panel, 1)  # 1 is the stretch factor

        # Set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize and start the watcher thread
        self.watcher_thread = WatcherThread("C:/AutoSavePro/Saves")
        self.watcher_thread.log_signal.connect(self.update_log)
        self.watcher_thread.start()

    def add_app_item(self, app_name, icon_name):
        item = QListWidgetItem(self.app_list)
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 10, 10, 10)

        icon_label = QLabel()
        icon_path = os.path.join("AutoSavePro", "autosave", "icons", icon_name)
        icon_pixmap = QPixmap(icon_path)
        icon_label.setPixmap(icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        item_layout.addWidget(icon_label)

        name_label = QLabel(app_name)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        item_layout.addWidget(name_label)

        item_layout.addStretch()

        freq_combo = QComboBox()
        freq_combo.addItems(["05min", "10min", "15min", "1h"])
        freq_combo.setStyleSheet("""
            QComboBox {
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-width: 100px;
                font-size: 16px;
                color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #555555;
                border-left-style: solid;
            }
        """)
        freq_combo.currentTextChanged.connect(lambda freq: self.change_save_frequency(app_name, freq))
        item_layout.addWidget(freq_combo)

        item_layout.addSpacing(20)

        switch = OnOffSwitch()
        switch.stateChanged.connect(lambda state: self.toggle_app_watching(app_name, state))
        item_layout.addWidget(switch)

        item.setSizeHint(item_widget.sizeHint())
        self.app_list.setItemWidget(item, item_widget)

    def add_new_application(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Sélectionner l'application", "", "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            app_name = os.path.basename(fileName)
            self.add_app_item(app_name, "plus.png")
            # Add the application to the watcher
            try:
                self.watcher_thread.watcher.add_application(app_name, [".txt"])
                self.update_log(f"Added new application to watch: {app_name}")
            except Exception as e:
                self.update_log(f"Error adding application {app_name}: {str(e)}")       

    def update_log(self, message):
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    def change_save_frequency(self, app_name, frequency):
        # Convertir la fréquence en secondes
        freq_map = {"05min": 300, "10min": 600, "15min": 900, "1h": 3600}
        seconds = freq_map.get(frequency, 300)  # default to 5 minutes
        self.watcher_thread.watcher.set_save_frequency(app_name, seconds)
        self.update_log("Changed save frequency for {} to {}".format(app_name, frequency))

    def toggle_app_watching(self, app_name, state):
        if state:
            self.watcher_thread.watcher.add_application(app_name, [".txt"])
            self.update_log("Started watching {}".format(app_name))
        else:
            self.watcher_thread.watcher.stop_watching_app(app_name)
            self.update_log("Stopped watching {}".format(app_name))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())