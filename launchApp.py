import os
import sys
import json
import subprocess
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGroupBox, QGridLayout, QComboBox, QPushButton, QDialog, QLabel
)
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, QThread, Signal


def find_executable(application):
    """
    Finds the application path from json file which will have the application names with the application paths
    :param application: (str) Application name to search in the json file
    :return:
        (str): Returns selected application path, if application name not found or path doesn't exists then dialog box
                will be displayed
    """
    working_dir = os.path.dirname(__file__)
    app_json_path = os.path.join(working_dir, "app_paths.json")
    with open(app_json_path, 'r') as fd:
        data = json.load(fd)
    if data.get(application, None):
        app_path = data.get(application)
        if os.path.exists(app_path):
            return data.get(application)
        else:
            dialog = ErrorDialog(
                "Invalid application path",
                "Invalid application path in the json file named {1}. Please update the application"
                " path for {0} in the \"app_paths.json\" file".format(application, app_path)
            )
            dialog.exec_()
    else:
        dialog = ErrorDialog(
            "Invalid Application",
            "Unable to find the application name in the json file named {0}. Please add the application"
            " data in the \"app_paths.json\" file".format(application)
        )
        dialog.exec_()


class AppExecutor(QThread):
    """
    Thread to run the application without any app freeze
    :param finished: (Qt.Signal) Signal to raise once the process is completed
    """
    finished = Signal()

    def __init__(self, command):
        """
        Constructor to initialize thread
        :param command: (str) Command to execute the application
        """
        super().__init__()
        self.command = command

    def run(self):
        """
        Strats the thread process
        :return:
        """
        try:
            subprocess.call(self.command, shell=True)
        except subprocess.CalledProcessError as e:
            print("Error occured: " + str(e))

        self.finished.emit()


class ErrorDialog(QDialog):
    def __init__(self, title, text):
        super().__init__()

        self.setWindowTitle(title)
        self.setFixedSize(500, 100)

        self.label = QLabel(self)
        self.label.setText(text)
        self.label.setWordWrap(True)

        self.ok_btn = QPushButton(self)
        self.ok_btn.setText("OK")
        self.ok_btn.clicked.connect(self.close)

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.label, 0, 0, 1, 3)
        layout.addWidget(self.ok_btn, 1, 2, 1, 1)


class LaunchApp(QMainWindow):
    """
    Main window to display the application process
    """
    def __init__(self):
        """
        Initialize basic QMainwindow attributes
        """
        super().__init__()

        self.setWindowTitle("Propel")

        main_widget = QWidget(self)
        layout = QGridLayout()
        main_widget.setLayout(layout)

        self.project_details = QComboBox(self)
        self.project_details.addItems(["TEST_PROJECT"])

        self.perspective_group = GroupLauncher("Perspective", self)
        self.perspective_group.add_launch_item(
            r"F:\Programming\test-update\icons\Autodesk-Maya-logo.jpg", "\"{0}\"".format(find_executable("maya"))
        )

        self.composition_group = GroupLauncher("Composition", self)
        self.composition_group.add_launch_item(
            r"F:\Programming\test-update\icons\nuke.jpg", "\"{0}\"".format(find_executable("nuke"))
        )

        self.apps_group = GroupLauncher("Apps", self)

        layout.addWidget(self.project_details, 0, 1, 1, 1)
        layout.addWidget(self.perspective_group, 1, 0, 1, 3)
        layout.addWidget(self.composition_group, 2, 0, 1, 3)
        layout.addWidget(self.apps_group, 3, 0, 1, 3)

        self.setCentralWidget(main_widget)


class GroupLauncher(QGroupBox):
    """
    Redundant QGroupBox widget
    """

    def __init__(self, title, parent):
        """
        Initializing QGroupBox widget
        :param title: (str) Title for the group box
        :param parent: (QWidget) Widget to parent the group box
        """
        super().__init__(title, parent)

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

    def add_launch_item(self, icon_path, command):
        """
        Creates the button once this method is called and connects the command to be executed
        :param icon_path: (str) Image path to set the icon to the QPushButton
        :param command: (str) Command to run once button is clicked
        """
        button = QPushButton(self)
        icon = QPixmap(icon_path)
        scaled_icon = icon.scaled(100, 100)
        button.setIconSize(scaled_icon.size())
        button.setIcon(icon)
        button.setFixedSize(100, 100)
        self.layout.addWidget(button, 0, 0, 1, 1)

        if command == "\"None\"":
            button.setEnabled(False)

        button.clicked.connect(lambda: self.run_command(command, button))

    def run_command(self, command, button):
        """
        Runs the command collaboratively with QThread
        :param command: (str) Command to run once button is clicked
        :param button: (QPushButton) Button to disable once the application run is in progress
        """
        button.setEnabled(False)
        print(f"executing the command {command}")
        self.executor = AppExecutor(command)
        self.executor.finished.connect(lambda: self.app_opened(button))
        self.executor.start()

    def app_opened(self, button):
        """
        Enables the button once the process is completed
        :param button: (QPushButton) Button to disable once the application run is in progress
        """
        button.setEnabled(True)
        print("Application opened")


if __name__ == '__main__':
    app = QApplication([])
    launcher = LaunchApp()
    launcher.show()
    sys.exit(app.exec_())
