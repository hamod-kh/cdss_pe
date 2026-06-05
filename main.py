from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import sys
from gui.main_window import MainWindow
from logger.logger import get_logger


def main() -> None:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("CDS PE")
    app.setOrganizationName("University CDSS Project")

    log = get_logger()
    log.info("Application starting…")

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    log.info(f"Application exiting (code {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
