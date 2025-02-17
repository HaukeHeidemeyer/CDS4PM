from gui.main import MainWindow
import logging
from PyQt6.QtWidgets import QApplication
import sys
import numpy as np

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Debug mode
    debug_mode = True  # Set this to True to enable debug mode, False to disable
    pickle_file_path = "resources_data.pickle"

    # Create a file handler
    handler = logging.FileHandler('app.log')

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    logger.info("Starting the application")
    app = QApplication(sys.argv)
    window = MainWindow(debug_mode=False, pickle_file_path=pickle_file_path)
    window.show()
    sys.exit(app.exec())
