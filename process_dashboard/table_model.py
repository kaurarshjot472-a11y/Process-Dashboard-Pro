"""Qt model for displaying process snapshots."""
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor
from .config import CPU_ALERT, MEMORY_ALERT_BYTES, format_bytes

class ProcessTableModel(QAbstractTableModel):

    """Qt model/view avoids destroying and recreating every table item per sample."""

    HEADERS = ["Process name", "PID", "State", "CPU", "Memory", "Threads", "Alert"]



    def __init__(self, parent=None):

        super().__init__(parent)

        self.rows = []

        self.pid_to_row = {}



    def rowCount(self, parent=QModelIndex()):

        return 0 if parent.isValid() else len(self.rows)



    def columnCount(self, parent=QModelIndex()):

        return 0 if parent.isValid() else len(self.HEADERS)



    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:

            if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.HEADERS):

                return self.HEADERS[section]

            if orientation == Qt.Orientation.Vertical:

                return str(section + 1)

        return None



    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if not index.isValid() or not (0 <= index.row() < len(self.rows)):

            return None

        row = self.rows[index.row()]

        col = index.column()

        cpu = row["cpu"]

        rss = row["rss"]

        alert = "High CPU" if cpu >= CPU_ALERT else ("High RAM" if rss >= MEMORY_ALERT_BYTES else "—")

        values = [

            row["name"], str(row["pid"]), row["status"].title(),

            f"{cpu:.1f}%", format_bytes(rss), str(row["threads"]), alert

        ]

        if role == Qt.ItemDataRole.DisplayRole:

            return values[col]

        if role == Qt.ItemDataRole.UserRole:

            return row["pid"]

        if role == Qt.ItemDataRole.TextAlignmentRole and col in (1, 3, 4, 5):

            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if role == Qt.ItemDataRole.ForegroundRole:

            if col == 2 and row["status"].casefold() in ("stopped", "suspended"):

                return QColor("#e9c46a")

            if col == 6 and alert != "—":

                return QColor("#ffb86c")

        if role == Qt.ItemDataRole.ToolTipRole:

            return f'{row["name"]} (PID {row["pid"]})'

        return None



    def set_rows(self, rows):

        # Keep view/selection stable. Reset is much cheaper than allocating

        # hundreds of QTableWidgetItems every refresh, but a full diff model

        # would be the next optimization for extremely large process lists.

        self.beginResetModel()

        self.rows = rows

        self.pid_to_row = {row["pid"]: i for i, row in enumerate(rows)}

        self.endResetModel()



    def row_for_pid(self, pid):

        return self.pid_to_row.get(pid)
