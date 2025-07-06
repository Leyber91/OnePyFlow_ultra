# gui_v2/worker.py

from PyQt5 import QtCore
import logging

# Import the orchestrator
from OneFlow.oneflow import OneFlow_MainFunction
from .qt_handler import QtHandler

class Worker(QtCore.QThread):
    """
    A QThread-based worker that orchestrates the OneFlow data collection.
    It accepts:
      - site, sos (start datetime), eos (end datetime),
      - plan_type, shift,
      - modules (optional list of modules to run).
    """
    log = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, site, sos, eos, plan_type, shift, modules=None):
        super().__init__()
        self.site = site
        self.sos = sos
        self.eos = eos
        self.plan_type = plan_type
        self.shift = shift
        # If modules is None or empty, you could interpret "run all modules"
        # but by default we store them as given:
        self.modules = modules or []
        self._is_running = True

        # Set up a custom logging handler that emits to the GUI
        self.qt_handler = QtHandler()
        self.qt_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.qt_handler.log_signal.connect(self.log.emit)

        # Attach the handler to the root logger
        logging.getLogger().addHandler(self.qt_handler)

    def run(self):
        try:
            # Convert self.sos/self.eos to strings if they're datetime objects
            # in "YYYY-MM-DD HH:MM:SS" format (or adapt as needed).
            if hasattr(self.sos, 'strftime'):
                sdt_str = self.sos.strftime("%Y-%m-%d %H:%M:%S")
            else:
                sdt_str = str(self.sos)

            if hasattr(self.eos, 'strftime'):
                edt_str = self.eos.strftime("%Y-%m-%d %H:%M:%S")
            else:
                edt_str = str(self.eos)

            # Call the main orchestration function with modules
            output_file = OneFlow_MainFunction(
                Site=self.site,
                SOSdatetime=sdt_str,
                EOSdatetime=edt_str,
                plan_type=self.plan_type,
                shift=self.shift,
                modules=self.modules
            )

            if output_file:
                self.log.emit(
                    f"Data collection for {self.site} (Plan={self.plan_type}, Shift={self.shift}) "
                    f"completed successfully.\nOutput: {output_file}"
                )
            else:
                self.log.emit(
                    f"Data collection for {self.site} (Plan={self.plan_type}, Shift={self.shift}) "
                    f"did NOT produce an output file."
                )

        except Exception as e:
            self.log.emit(
                f"An error occurred while processing {self.site} "
                f"(Plan={self.plan_type}, Shift={self.shift}): {e}"
            )
        finally:
            # Signal that the thread is done
            self.finished.emit()
            # Remove our QtHandler to avoid duplicate log emissions
            logging.getLogger().removeHandler(self.qt_handler)

    def write(self, message):
        """ If something writes directly to this worker as a stream, we emit it as logs. """
        self.log.emit(message)

    def flush(self):
        """ No-op for stream interface. """
        pass

    def stop(self):
        """ Graceful stop if needed. """
        self._is_running = False
        self.quit()
        self.wait()
