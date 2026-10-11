"""Main dashboard window and UI event handlers."""
import os
from datetime import datetime
import psutil
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHeaderView, QStatusBar, QTableView, QTextEdit,
    QComboBox, QStackedWidget, QListWidget, QListWidgetItem, QGridLayout,
    QAbstractItemView
)
from .config import APP_NAME, SAMPLE_INTERVAL, CPU_ALERT, MEMORY_ALERT_BYTES, PROTECTED_NAMES, format_bytes, safe_name
from .monitor import ProcessMonitor
from .table_model import ProcessTableModel
from .widgets import MetricCard, LiveGraph
from .theme import STYLESHEET

class Dashboard(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("ProcessDesk  |  System Intelligence")

        self.resize(1280, 800)

        self.setMinimumSize(980, 620)

        self.rows_by_pid = {}

        self.latest_snapshot = None

        self._build_ui()

        self._apply_theme()

        self.monitor = ProcessMonitor()

        self.monitor.snapshot_ready.connect(self.update_snapshot)

        self.monitor.monitor_error.connect(self.show_monitor_error)

        self.monitor.start()

        self.update_controls()



    def _build_ui(self):

        shell = QWidget()

        shell_layout = QHBoxLayout(shell)

        shell_layout.setContentsMargins(0, 0, 0, 0)

        shell_layout.setSpacing(0)



        sidebar = QListWidget()

        sidebar.setObjectName("sidebar")

        sidebar.setFixedWidth(220)

        for label, icon in [("Overview", "◈"), ("Processes", "☷"), ("Performance", "▥")]:

            item = QListWidgetItem(f"{icon}   {label}")

            item.setSizeHint(item.sizeHint())

            sidebar.addItem(item)

        sidebar.setCurrentRow(0)

        shell_layout.addWidget(sidebar)



        content = QWidget()

        root = QVBoxLayout(content)

        root.setContentsMargins(28, 24, 28, 20)

        root.setSpacing(20)

        heading = QHBoxLayout()

        title_box = QVBoxLayout()

        self.page_title = QLabel("Overview")

        self.page_title.setObjectName("title")

        subtitle = QLabel("Live system intelligence  /  Resource monitoring")

        subtitle.setObjectName("subtitle")

        title_box.addWidget(self.page_title)

        title_box.addWidget(subtitle)

        heading.addLayout(title_box)

        heading.addStretch()

        self.last_update = QLabel("●  Connecting to system…")

        self.last_update.setObjectName("liveStatus")

        heading.addWidget(self.last_update)

        root.addLayout(heading)



        self.pages = QStackedWidget()

        self.overview_page = self._build_overview_page()

        self.processes_page = self._build_processes_page()

        self.performance_page = self._build_performance_page()

        self.pages.addWidget(self.overview_page)

        self.pages.addWidget(self.processes_page)

        self.pages.addWidget(self.performance_page)

        root.addWidget(self.pages, 1)

        shell_layout.addWidget(content, 1)

        self.setCentralWidget(shell)

        sidebar.currentRowChanged.connect(self.change_page)

        self.setStatusBar(QStatusBar(self))

        self.statusBar().showMessage("Starting background monitor…")

        file_menu = self.menuBar().addMenu("&File")

        refresh_action = QAction("Refresh now", self)

        refresh_action.setShortcut("F5")

        refresh_action.triggered.connect(self.refresh_now)

        file_menu.addAction(refresh_action)

        exit_action = QAction("Exit", self)

        exit_action.setShortcut("Ctrl+Q")

        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)



    def _build_overview_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(0, 0, 0, 0)

        cards = QHBoxLayout()

        self.cpu_card = MetricCard("CPU usage", "Total processor utilization")

        self.ram_card = MetricCard("Memory", "Physical memory in use")

        self.process_card = MetricCard("Processes", "Processes detected")

        self.issue_card = MetricCard("Potential issues", "High CPU / memory alerts")

        for card in (self.cpu_card, self.ram_card, self.process_card, self.issue_card):

            cards.addWidget(card)

        layout.addLayout(cards)

        self.overview_cpu_graph = LiveGraph("CPU utilization", "%", 100)

        self.overview_ram_graph = LiveGraph("Memory utilization", "%", 100)

        grid = QGridLayout()

        grid.addWidget(self.overview_cpu_graph, 0, 0)

        grid.addWidget(self.overview_ram_graph, 0, 1)

        layout.addLayout(grid)

        note = QLabel("Potential issue heuristics: sampled CPU ≥ 25% or process memory ≥ 500 MB. Adjust thresholds in main.py.")

        note.setObjectName("note")

        note.setWordWrap(True)

        layout.addWidget(note)

        layout.addStretch()

        return page



    def _build_processes_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(0, 0, 0, 0)

        controls = QHBoxLayout()

        self.search = QLineEdit()

        self.search.setPlaceholderText("Search process name or PID…")

        self.search.setClearButtonEnabled(True)

        self.search.textChanged.connect(self.render_table)

        controls.addWidget(self.search, 1)

        self.state_filter = QComboBox()

        self.state_filter.addItems(["All states", "Running", "Sleeping", "Stopped", "Zombie", "Disk-sleep"])

        self.state_filter.currentTextChanged.connect(self.render_table)

        controls.addWidget(self.state_filter)

        self.suspend_btn = QPushButton("⏸ Suspend")

        self.resume_btn = QPushButton("▶ Resume")

        self.end_btn = QPushButton("■ End task")

        self.refresh_btn = QPushButton("↻ Refresh")

        self.suspend_btn.clicked.connect(self.suspend_process)

        self.resume_btn.clicked.connect(self.resume_process)

        self.end_btn.clicked.connect(self.terminate_process)

        self.refresh_btn.clicked.connect(self.refresh_now)

        for btn in (self.suspend_btn, self.resume_btn, self.end_btn, self.refresh_btn):

            controls.addWidget(btn)

        layout.addLayout(controls)



        self.table = QTableView()

        self.model = ProcessTableModel(self)

        self.table.setModel(self.model)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.setAlternatingRowColors(True)

        self.table.setSortingEnabled(False)  # data arrives pre-sorted; avoids costly view sorting each update

        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setWordWrap(False)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        for col in range(1, 7):

            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(col, {1: 85, 2: 105, 3: 90, 4: 115, 5: 95, 6: 125}[col])

        self.table.selectionModel().selectionChanged.connect(self.update_controls)

        self.table.doubleClicked.connect(self.show_details)

        layout.addWidget(self.table, 1)

        self.details = QTextEdit()

        self.details.setReadOnly(True)

        self.details.setMaximumHeight(105)

        self.details.setPlaceholderText("Select a process; double-click a row for details.")

        layout.addWidget(self.details)

        safety = QLabel("Suspend can freeze an application; termination can lose unsaved work. Windows may deny protected-process access.")

        safety.setObjectName("note")

        safety.setWordWrap(True)

        layout.addWidget(safety)

        return page



    def _build_performance_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(0, 0, 0, 0)

        intro = QLabel("System performance • live samples, approximately once per second")

        intro.setObjectName("subtitle")

        layout.addWidget(intro)

        grid = QGridLayout()

        self.cpu_graph = LiveGraph("CPU", "%", 100)

        self.memory_graph = LiveGraph("Memory", "%", 100)

        self.disk_read_graph = LiveGraph("Disk read", "MB/s", None)

        self.disk_write_graph = LiveGraph("Disk write", "MB/s", None)

        self.net_recv_graph = LiveGraph("Network receive", "MB/s", None)

        self.net_send_graph = LiveGraph("Network send", "MB/s", None)

        graphs = [

            self.cpu_graph, self.memory_graph, self.disk_read_graph,

            self.disk_write_graph, self.net_recv_graph, self.net_send_graph

        ]

        for i, graph in enumerate(graphs):

            grid.addWidget(graph, i // 2, i % 2)

        layout.addLayout(grid, 1)

        return page



    def _apply_theme(self):
        self.setStyleSheet(STYLESHEET)
        self.end_btn.setObjectName("danger")
        self.end_btn.style().unpolish(self.end_btn)
        self.end_btn.style().polish(self.end_btn)

    def change_page(self, index):

        if index < 0:

            return

        self.pages.setCurrentIndex(index)

        self.page_title.setText(["Overview", "Processes", "Performance"][index])



    def refresh_now(self):

        self.monitor.request_refresh()

        self.statusBar().showMessage("Requested an early sample.", 2000)



    def show_monitor_error(self, message):

        self.statusBar().showMessage(f"Monitor warning: {message}", 5000)



    def update_snapshot(self, snapshot):

        self.latest_snapshot = snapshot

        self.rows_by_pid = {r["pid"]: r for r in snapshot["rows"]}

        self.cpu_card.value.setText(f'{snapshot["cpu_total"]:.0f}%')

        self.ram_card.value.setText(f'{snapshot["memory_percent"]:.0f}%')

        self.ram_card.subtext.setText(

            f'{format_bytes(snapshot["memory_used"])} used / {format_bytes(snapshot["memory_total"])}'

        )

        self.process_card.value.setText(str(snapshot["process_count"]))

        issues = [r for r in snapshot["rows"] if r["cpu"] >= CPU_ALERT or r["rss"] >= MEMORY_ALERT_BYTES]

        self.issue_card.value.setText(str(len(issues)))

        self.issue_card.subtext.setText("Above configured thresholds")

        self.last_update.setText(f'●  LIVE  ·  {snapshot["timestamp"]}')



        # Keep graph redraws lightweight; only append one point per snapshot.

        self.overview_cpu_graph.add_value(snapshot["cpu_total"])

        self.overview_ram_graph.add_value(snapshot["memory_percent"])

        self.cpu_graph.add_value(snapshot["cpu_total"])

        self.memory_graph.add_value(snapshot["memory_percent"])

        self.disk_read_graph.add_value(snapshot["disk_read_rate"] / (1024 * 1024))

        self.disk_write_graph.add_value(snapshot["disk_write_rate"] / (1024 * 1024))

        self.net_recv_graph.add_value(snapshot["net_recv_rate"] / (1024 * 1024))

        self.net_send_graph.add_value(snapshot["net_sent_rate"] / (1024 * 1024))

        self.render_table()

        self.statusBar().showMessage(

            f'{snapshot["process_count"]} processes detected • Sample interval {SAMPLE_INTERVAL:.1f}s'

        )



    def render_table(self, *_):

        if not hasattr(self, "model") or self.latest_snapshot is None:

            return

        query = self.search.text().strip().casefold()

        state = self.state_filter.currentText()

        old_pid = self.selected_pid()

        rows = []

        for row in self.latest_snapshot["rows"]:

            if query and query not in row["name"].casefold() and query not in str(row["pid"]):

                continue

            if state != "All states" and row["status"].casefold() != state.casefold():

                continue

            rows.append(row)

        rows.sort(key=lambda r: r["name"].casefold())

        self.model.set_rows(rows)

        if old_pid is not None:

            row_index = self.model.row_for_pid(old_pid)

            if row_index is not None:

                self.table.selectRow(row_index)

        self.update_controls()



    def selected_pid(self):

        selection = self.table.selectionModel().selectedRows()

        if not selection:

            return None

        row = selection[0].row()

        if 0 <= row < len(self.model.rows):

            return self.model.rows[row]["pid"]

        return None



    def update_controls(self, *_):

        pid = self.selected_pid() if hasattr(self, "model") else None

        enabled = pid is not None and pid in self.rows_by_pid

        for btn in (self.suspend_btn, self.resume_btn, self.end_btn):

            btn.setEnabled(enabled)



    def validated_target(self):

        pid = self.selected_pid()

        if pid is None:

            QMessageBox.information(self, "Select a process", "Select a process from the table first.")

            return None

        if pid <= 4 or pid == os.getpid():

            QMessageBox.warning(self, "Protected process", "This demo blocks core low PIDs and itself.")

            return None

        try:

            proc = psutil.Process(pid)

            name = (proc.name() or "").casefold()

            if name in PROTECTED_NAMES:

                QMessageBox.warning(self, "Protected process", f"'{proc.name()}' is on the protected-process list.")

                return None

            return proc, proc.create_time()

        except psutil.NoSuchProcess:

            QMessageBox.information(self, "Process ended", "That process no longer exists. Wait for the next sample.")

        except psutil.AccessDenied:

            QMessageBox.warning(self, "Access denied", "Windows denied access to this process.")

        except (psutil.Error, OSError) as exc:

            QMessageBox.warning(self, "Could not inspect process", str(exc))

        return None



    @staticmethod

    def still_same_process(proc, created):

        try:

            return proc.is_running() and abs(proc.create_time() - created) < 0.01

        except (psutil.Error, OSError):

            return False



    def suspend_process(self):

        target = self.validated_target()

        if not target:

            return

        proc, created = target

        name, pid = safe_name(proc), proc.pid

        if QMessageBox.question(

            self, "Suspend process", f"Suspend '{name}' (PID {pid})?\nIt may freeze until resumed.",

            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,

            QMessageBox.StandardButton.No

        ) != QMessageBox.StandardButton.Yes:

            return

        if not self.still_same_process(proc, created):

            QMessageBox.warning(self, "Process changed", "The process exited or changed. Select it again.")

            return

        try:

            proc.suspend()

            self.statusBar().showMessage(f"Suspend request sent to PID {pid}.", 4000)

        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error, OSError) as exc:

            QMessageBox.warning(self, "Suspend failed", str(exc))



    def resume_process(self):

        target = self.validated_target()

        if not target:

            return

        proc, created = target

        if not self.still_same_process(proc, created):

            QMessageBox.warning(self, "Process changed", "The process exited or changed. Select it again.")

            return

        try:

            proc.resume()

            self.statusBar().showMessage(f"Resume request sent to PID {proc.pid}.", 4000)

        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error, OSError) as exc:

            QMessageBox.warning(self, "Resume failed", str(exc))



    def terminate_process(self):

        target = self.validated_target()

        if not target:

            return

        proc, created = target

        pid, name = proc.pid, safe_name(proc)

        if QMessageBox.warning(

            self, "End task?", f"Terminate '{name}' (PID {pid})?\n\nUnsaved work may be lost.",

            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,

            QMessageBox.StandardButton.No

        ) != QMessageBox.StandardButton.Yes:

            return

        if not self.still_same_process(proc, created):

            QMessageBox.warning(self, "Process changed", "The process exited or changed. Select it again.")

            return

        try:

            proc.terminate()

            try:

                proc.wait(timeout=0)

                self.statusBar().showMessage(f"PID {pid} exited.", 4000)

            except psutil.TimeoutExpired:

                self.statusBar().showMessage("Termination requested; no force-kill was sent.", 4000)

        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.Error, OSError) as exc:

            QMessageBox.warning(self, "Termination failed", str(exc))



    def show_details(self, index):

        if not index.isValid():

            return

        pid = self.selected_pid()

        if pid is None:

            return

        try:

            proc = psutil.Process(pid)

            row = self.rows_by_pid.get(pid, {})

            with proc.oneshot():

                name = proc.name()

                exe = proc.exe()

                user = proc.username()

                status = proc.status()

                started = datetime.fromtimestamp(proc.create_time()).strftime("%Y-%m-%d %H:%M:%S")

                mem = proc.memory_info()

                command = " ".join(proc.cmdline())

                threads = proc.num_threads()

                ppid = proc.ppid()

            self.details.setPlainText(

                f"Name: {name} | PID: {pid} | Parent PID: {ppid} | State: {status}\n"

                f"User: {user} | Threads: {threads} | Started: {started}\n"

                f"CPU: {row.get('cpu', 0):.1f}% | RSS memory: {format_bytes(mem.rss)}\n"

                f"Executable: {exe}\nCommand: {command}"

            )

        except psutil.AccessDenied:

            self.details.setPlainText("Windows denied access to some details.")

        except psutil.NoSuchProcess:

            self.details.setPlainText("The process has already exited.")

        except (psutil.Error, OSError) as exc:

            self.details.setPlainText(f"Could not read details: {exc}")



    def closeEvent(self, event):

        if hasattr(self, "monitor") and self.monitor.isRunning():

            self.monitor.stop()

            self.monitor.wait(3000)

        super().closeEvent(event)
