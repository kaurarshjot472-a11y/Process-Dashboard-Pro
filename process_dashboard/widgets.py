"""Reusable dashboard cards and lightweight live graphs."""
from collections import deque
from PySide6.QtCore import Qt, QPointF, QMargins
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from .config import GRAPH_POINTS

class MetricCard(QFrame):

    def __init__(self, title, subtitle):

        super().__init__()

        self.setObjectName("metricCard")

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 17, 20, 17)

        self.heading = QLabel(title.upper())

        self.heading.setObjectName("metricLabel")

        self.value = QLabel("—")

        self.value.setObjectName("metricValue")

        self.subtext = QLabel(subtitle)

        self.subtext.setObjectName("muted")

        layout.addWidget(self.heading)

        layout.addWidget(self.value)

        layout.addWidget(self.subtext)


class LiveGraph(QFrame):

    def __init__(self, title, unit, max_y=100, parent=None):

        super().__init__(parent)

        self.setObjectName("graphCard")

        self._unit = unit

        self._fixed_max = max_y

        self._points = deque(maxlen=GRAPH_POINTS)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(18, 14, 18, 12)

        header = QHBoxLayout()

        label = QLabel(title)

        label.setObjectName("graphTitle")

        self.current = QLabel("—")

        self.current.setObjectName("graphCurrent")

        header.addWidget(label)

        header.addStretch()

        header.addWidget(self.current)

        layout.addLayout(header)



        self.series = QLineSeries()

        self.series.setName(title)
        pen = QPen(QColor("#61b9ff" if max_y is not None else "#55d8bb"))
        pen.setWidth(2)
        self.series.setPen(pen)

        self.chart = QChart()

        self.chart.addSeries(self.series)

        self.chart.legend().hide()

        self.chart.setTitle("")

        self.chart.setBackgroundVisible(False)

        self.chart.setPlotAreaBackgroundVisible(False)

        self.chart.setMargins(QMargins(3, 3, 3, 3))

        self.axis_x = QValueAxis()

        self.axis_x.setRange(0, GRAPH_POINTS - 1)

        self.axis_x.setLabelsVisible(False)

        self.axis_x.setGridLineVisible(False)

        self.axis_y = QValueAxis()

        # Fixed range for percentages; auto-scale throughput graphs (disk/network).

        self.axis_y.setRange(0.0, float(max_y) if max_y is not None else 10.0)

        self.axis_y.setLabelFormat("%.0f")

        self.axis_y.setLabelsColor(QColor("#8ea5c5"))

        self.axis_y.setGridLineColor(QColor("#263955"))

        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)

        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)

        self.series.attachAxis(self.axis_x)

        self.series.attachAxis(self.axis_y)

        self.chart_view = QChartView(self.chart)

        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        self.chart_view.setMinimumHeight(170)

        layout.addWidget(self.chart_view)



    def add_value(self, value):

        value = max(0.0, float(value))

        self._points.append(value)

        self.current.setText(f"{value:.1f} {self._unit}" if self._unit else f"{value:.1f}")

        points = [QPointF(float(i), float(v)) for i, v in enumerate(self._points)]

        self.series.replace(points)

        self.axis_x.setRange(0, max(GRAPH_POINTS - 1, len(points) - 1))

        if self._fixed_max is not None:

            self.axis_y.setRange(0.0, float(self._fixed_max))

        else:

            upper = max(10.0, max(self._points, default=10.0) * 1.2)

            self.axis_y.setRange(0.0, upper)
