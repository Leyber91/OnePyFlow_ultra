# gui_v2.py
# ----------------------------------------------------------------------------
# A PyQt5 GUI for OneFlow data collector. This version ensures that if the UI is
# used, all modules are executed (or a configurable subset).
# ----------------------------------------------------------------------------

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import logging
from datetime import datetime, timedelta

from .worker import Worker
from .qt_handler import QtHandler
from utils.shared_resources import FC_CONFIGS

ALL_MODULES = [
    "DockMaster", "DockMaster2", "DockFlow", "Galaxy", "Galaxy2", "ICQA",
   "F2P", "kNekro", "SSP", "PPR", "ALPS", "ALPS_RC_Sort",
   "RODEO", "FMC", "QuipCSV", "YMS"
]
### # A constant with all known modules to run from the UI (if you want everything):
### ALL_MODULES = [
###     "YMS", "FMC"
### ]
# A constant with all known modules to run from the UI (if you want everything):
### ALL_MODULES = [
###     "DockMaster", "DockMaster2"
### ]

class OneFlowGUI(QtWidgets.QWidget):
    """
    Main PyQt widget for the OneFlow data collector GUI.
    When the user clicks "Run", it launches a Worker thread that runs
    OneFlow_MainFunction with all modules (or a subset) for the chosen site/shift.
    """

    log_signal = QtCore.pyqtSignal(str)
    enable_run_button_signal = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.current_theme = "amazon"
        self.selected_site = None
        self.worker = None
        self.selected_plan_type = 'Prior-Day'

        # Connect signals
        self.log_signal.connect(self.log_message)
        self.enable_run_button_signal.connect(self._enable_run_button)

        self.initUI()
        self.apply_theme(self.current_theme)

    def initUI(self):
        """
        Set up the main UI components: site buttons, date pickers, shift combos,
        plan type selectors, and the terminal output area.
        """
        self.setWindowTitle('OneFlow Data Collector')
        self.setMinimumWidth(900)
        self.setMinimumHeight(580)

        # Main layout
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel (Scrollable) -------------------------------
        left_panel = QtWidgets.QWidget()
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(450)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        # Sites panel toggle
        self.toggle_site_button = QtWidgets.QPushButton("≡ Sites Panel")
        self.toggle_site_button.setObjectName("toggle_site_button")
        self.toggle_site_button.setCheckable(True)
        self.toggle_site_button.setChecked(True)
        self.toggle_site_button.clicked.connect(self.toggle_sites_panel)
        left_layout.addWidget(self.toggle_site_button, alignment=QtCore.Qt.AlignTop)

        # Sites container (Flow layout) -------------------------
        sites_container = QtWidgets.QWidget()
        sites_container.setObjectName("sites_container")
        flow_layout = FlowLayout(sites_container)
        flow_layout.setSpacing(8)

        self.site_buttons = {}
        for site in FC_CONFIGS.keys():
            button = QtWidgets.QPushButton(site)
            button.setCheckable(True)
            button.setFixedHeight(40)
            button.clicked.connect(self._on_site_selected)
            self.site_buttons[site] = button
            flow_layout.addWidget(button)

        sites_group = QtWidgets.QGroupBox("Select Site")
        sites_group.setObjectName("sites_group")
        sites_layout = QtWidgets.QVBoxLayout(sites_group)
        sites_layout.addWidget(sites_container)
        self.sites_group = sites_group
        left_layout.addWidget(sites_group)

        # Date & Shift selection card ---------------------------
        datetime_card = QtWidgets.QWidget()
        datetime_card.setObjectName("datetime_card")
        datetime_layout = QtWidgets.QVBoxLayout(datetime_card)
        datetime_layout.setContentsMargins(10, 10, 10, 10)
        datetime_layout.setSpacing(8)

        # Date selection
        date_label = QtWidgets.QLabel("Date:")
        self.date_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.update_times)

        date_row = QtWidgets.QHBoxLayout()
        date_row.addWidget(date_label)
        date_row.addWidget(self.date_edit)
        datetime_layout.addLayout(date_row)

        # Shift combo
        shift_label = QtWidgets.QLabel("Shift:")
        self.shift_combo = QtWidgets.QComboBox()
        self.shift_combo.currentIndexChanged.connect(self.update_times)

        shift_row = QtWidgets.QHBoxLayout()
        shift_row.addWidget(shift_label)
        shift_row.addWidget(self.shift_combo)
        datetime_layout.addLayout(shift_row)

        left_layout.addWidget(datetime_card)

        # Shift Timings (Collapsible) ---------------------------
        timings_group = CollapsibleBox("Shift Timings")
        timings_layout = QtWidgets.QFormLayout()
        timings_layout.setContentsMargins(10, 10, 10, 10)
        timings_layout.setSpacing(8)

        self.start_datetime = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.end_datetime   = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        timings_layout.addRow("Start:", self.start_datetime)
        timings_layout.addRow("End:", self.end_datetime)
        timings_group.setContentLayout(timings_layout)
        left_layout.addWidget(timings_group)

        # Plan type (Radio Buttons) -----------------------------
        plan_group = QtWidgets.QGroupBox("Plan Type")
        plan_layout = QtWidgets.QHBoxLayout(plan_group)
        plan_layout.setContentsMargins(10, 10, 10, 10)

        self.plan_buttons = {}
        for plan in ['Prior-Day', 'Next-Shift', 'SOS']:
            radio = QtWidgets.QRadioButton(plan)
            self.plan_buttons[plan] = radio
            plan_layout.addWidget(radio)
        # Default is 'Prior-Day'
        self.plan_buttons[self.selected_plan_type].setChecked(True)
        left_layout.addWidget(plan_group)

        # Action buttons ----------------------------------------
        actions_card = QtWidgets.QWidget()
        actions_card.setObjectName("actions_card")
        actions_layout = QtWidgets.QHBoxLayout(actions_card)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(12)

        self.run_button = QtWidgets.QPushButton("▶ Run")
        self.run_button.setObjectName("run_button")
        self.run_button.clicked.connect(self.run_process)

        self.exit_button = QtWidgets.QPushButton("✕ Exit")
        self.exit_button.setObjectName("exit_button")
        self.exit_button.clicked.connect(self.close_application)

        actions_layout.addWidget(self.run_button)
        actions_layout.addWidget(self.exit_button)
        left_layout.addWidget(actions_card)
        left_layout.addStretch()

        # Terminal section --------------------------------------
        terminal_widget = QtWidgets.QWidget()
        terminal_layout = QtWidgets.QVBoxLayout(terminal_widget)
        terminal_layout.setContentsMargins(16, 16, 16, 16)
        terminal_layout.setSpacing(8)

        terminal_header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(terminal_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        terminal_title = QtWidgets.QLabel("Terminal Output")
        terminal_title.setObjectName("terminal_title")
        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.setObjectName("clear_button")
        clear_button.clicked.connect(self._clear_terminal)

        header_layout.addWidget(terminal_title, 1)
        header_layout.addWidget(clear_button, 0, QtCore.Qt.AlignRight)
        terminal_layout.addWidget(terminal_header)

        self.terminal_display = QtWidgets.QTextEdit()
        self.terminal_display.setReadOnly(True)
        terminal_layout.addWidget(self.terminal_display, 1)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(scroll)
        splitter.addWidget(terminal_widget)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def apply_theme(self, theme_name):
        """
        Apply a QSS theme if found. Otherwise default style.
        """
        theme_file = os.path.join(os.path.dirname(__file__), 'themes', f'{theme_name}.qss')
        if os.path.exists(theme_file):
            with open(theme_file, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            self.log_signal.emit(f"Theme file '{theme_file}' not found. Using default style.")

    def _on_site_selected(self):
        """
        Called when a site button is clicked. Uncheck other sites, store the selected site,
        and refresh the shift combos.
        """
        sender = self.sender()
        site = sender.text()
        # Uncheck others
        for s, btn in self.site_buttons.items():
            if s != site:
                btn.setChecked(False)
        self.selected_site = site
        self.log_signal.emit(f"Site selected: {site}")
        self.update_shifts_for_site()

    def update_shifts_for_site(self):
        """
        Populate the shift combo based on the selected site config.
        Then call update_times() to fill in start/end times.
        """
        self.shift_combo.clear()
        if not self.selected_site:
            return
        site_config = FC_CONFIGS.get(self.selected_site)
        if not site_config:
            return

        shifts = site_config.get('shifts', [])
        # Populate combo with uppercase shift codes
        for shift in shifts:
            self.shift_combo.addItem(shift.upper())

        self.update_times()

    def toggle_sites_panel(self, checked):
        """
        Show/hide the 'Select Site' group box.
        """
        self.sites_group.setVisible(checked)

    def _clear_terminal(self):
        self.terminal_display.clear()

    def run_process(self):
        """
        Gathers user inputs (site, date/time, plan type, shift),
        then starts the Worker thread to run OneFlow_MainFunction.
        In this version, we run ALL_MODULES by default.
        """
        if self.worker is not None and self.worker.isRunning():
            self.log_signal.emit("A process is already running. Please wait until it finishes.")
            return

        if not self.selected_site:
            self.log_signal.emit("No site selected. Please select a site.")
            return

        # Get user-specified start/end times
        SOSdatetime = self.start_datetime.dateTime().toPyDateTime()
        EOSdatetime = self.end_datetime.dateTime().toPyDateTime()
        if SOSdatetime >= EOSdatetime:
            self.log_signal.emit("Invalid DateTime Range. Start must be before End.")
            return

        # Determine plan type from radio
        for plan, radio in self.plan_buttons.items():
            if radio.isChecked():
                self.selected_plan_type = plan
                break

        shift = self.shift_combo.currentText()


        # (Alternatively, you can define ALL_MODULES in this file,
        # but let's assume we import from worker or define it somewhere shared.)
        modules = ALL_MODULES

        # Create and start the worker
        self.worker = Worker(self.selected_site, SOSdatetime, EOSdatetime, self.selected_plan_type, shift, modules=modules)
        self.worker.log.connect(self.log_signal.emit)
        self.worker.finished.connect(self.thread_finished)
        self.run_button.setEnabled(False)
        self.worker.start()
        self.log_signal.emit(
            f"Started data collection for {self.selected_site}, Plan Type: {self.selected_plan_type}, "
            f"Shift: {shift}.\nRunning modules: {modules}"
        )

    def thread_finished(self):
        """
        Called when the Worker thread emits 'finished'. Re-enable the run button.
        """
        self.run_button.setEnabled(True)
        self.log_signal.emit("Processing completed.")

    def close_application(self):
        """
        Safely stop the worker (if running) and close the application.
        """
        if self.worker is not None and self.worker.isRunning():
            self.log_signal.emit("Waiting for the running process to finish...")
            self.worker.stop()
        QtWidgets.qApp.quit()

    def log_message(self, message):
        """
        Append a colored message to the terminal display.
        """
        color = "#FFFFFF"
        self.terminal_display.append(f"<span style='color: {color};'>{message}</span>")
        self.terminal_display.verticalScrollBar().setValue(
            self.terminal_display.verticalScrollBar().maximum()
        )

    def _enable_run_button(self, enable):
        """
        Slot to enable/disable the run button (if needed from external signals).
        """
        self.run_button.setEnabled(enable)

    def closeEvent(self, event):
        """
        Overridden to ensure we stop the worker if the user closes the window.
        """
        if self.worker is not None and self.worker.isRunning():
            self.log_signal.emit("Waiting for the running process to finish...")
            self.worker.stop()
        event.accept()

    def update_times(self):
        """
        Update self.start_datetime and self.end_datetime based on the selected site,
        shift schedule, and the chosen date from self.date_edit.
        """
        if not self.selected_site:
            return
        site_config = FC_CONFIGS.get(self.selected_site)
        if not site_config:
            return

        if self.shift_combo.count() == 0:
            return

        shift = self.shift_combo.currentText().lower()
        shift_hours = site_config['hours'].get(shift, {})
        date = self.date_edit.date().toPyDate()
        day_of_week = date.strftime('%A').lower()

        # Determine applicable schedule
        applicable_schedule = None
        for schedule_days, times in shift_hours.items():
            if ',' in schedule_days:
                days_list = [d.strip().lower() for d in schedule_days.split(',')]
            else:
                days_list = [schedule_days.lower()]

            for day in days_list:
                if day == 'alldays' or day == 'monsun':
                    applicable_schedule = times
                    break
                elif day == 'monsat' and day_of_week != 'sunday':
                    applicable_schedule = times
                    break
                elif day == 'monfri' and day_of_week not in ['saturday', 'sunday']:
                    applicable_schedule = times
                    break
                elif day == 'saturday' and day_of_week == 'saturday':
                    applicable_schedule = times
                    break
                elif day == 'sunday' and day_of_week == 'sunday':
                    applicable_schedule = times
                    break
                elif day == day_of_week:
                    applicable_schedule = times
                    break
            if applicable_schedule:
                break

        if not applicable_schedule:
            self.log_signal.emit(
                f"No schedule found for {self.selected_site} on {day_of_week.capitalize()} for shift {shift.upper()}"
            )
            return

        if not (isinstance(applicable_schedule, list) and len(applicable_schedule) == 2):
            self.log_signal.emit(
                f"Invalid schedule format for {self.selected_site} - {shift.upper()}"
            )
            return

        start_hour, end_hour = applicable_schedule

        # Build the start/end datetimes
        start_datetime = datetime.combine(date, datetime.min.time()) + timedelta(hours=start_hour)
        if end_hour < start_hour:
            # Spans past midnight
            end_datetime = datetime.combine(date, datetime.min.time()) + timedelta(hours=end_hour) + timedelta(days=1)
        else:
            end_datetime = datetime.combine(date, datetime.min.time()) + timedelta(hours=end_hour)

        # Update QDateTimeEdits
        self.start_datetime.setDateTime(QtCore.QDateTime(start_datetime))
        self.end_datetime.setDateTime(QtCore.QDateTime(end_datetime))

        # Log the updated times
        self.log_signal.emit(f"Shift times updated for {self.selected_site} - {shift.upper()}:")
        self.log_signal.emit(f"SOS: {start_datetime}")
        self.log_signal.emit(f"EoS: {end_datetime}")


# FlowLayout, CollapsibleBox for advanced layouts & collapsible sections
class FlowLayout(QtWidgets.QLayout):
    """
    A simple flow layout for site selection buttons.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.spacing_x = 8
        self.spacing_y = 8

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        return size

    def doLayout(self, rect, test_only=False):
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self.items:
            item_width = item.sizeHint().width()
            item_height = item.sizeHint().height()

            if x + item_width > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + self.spacing_y
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = x + item_width + self.spacing_x
            line_height = max(line_height, item_height)

        return y + line_height - rect.y()


class CollapsibleBox(QtWidgets.QWidget):
    """
    A collapsible box containing a title (toggle button) and a content area.
    """
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)
        self.content_area = QtWidgets.QScrollArea()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)

        self.toggle_button.clicked.connect(self.on_toggle)

    def on_toggle(self, checked):
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward if checked else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        """
        Replace the existing content layout with 'layout'.
        """
        if self.content_area.layout():
            old_layout = self.content_area.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            old_layout.deleteLater()

        self.content_area.setLayout(layout)
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = layout.sizeHint().height()

        self.toggle_animation.clear()

        # Animate the main widget's min/max height
        animation_min = QtCore.QPropertyAnimation(self, b"minimumHeight")
        animation_min.setDuration(200)
        animation_min.setStartValue(collapsed_height)
        animation_min.setEndValue(collapsed_height + content_height)

        animation_max = QtCore.QPropertyAnimation(self, b"maximumHeight")
        animation_max.setDuration(200)
        animation_max.setStartValue(collapsed_height)
        animation_max.setEndValue(collapsed_height + content_height)

        # Animate the content area
        animation_content = QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        animation_content.setDuration(200)
        animation_content.setStartValue(0)
        animation_content.setEndValue(content_height)

        self.toggle_animation.addAnimation(animation_min)
        self.toggle_animation.addAnimation(animation_max)
        self.toggle_animation.addAnimation(animation_content)
