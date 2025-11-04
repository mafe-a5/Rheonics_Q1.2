import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox, QDialog, QDialogButtonBox, QFormLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPainter, QColor, QBrush
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

BASE = os.path.dirname(__file__)

# Switch
class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        painter.setBrush(QBrush(QColor("#5BC4A2" if self.isChecked() else "#D3D5DA")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 14, 14)
        painter.setBrush(QBrush(QColor("white")))
        x = rect.width() - 24 if self.isChecked() else 4
        painter.drawEllipse(x, 4, 20, 20)

# Matplotlib
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=2.6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.fig.tight_layout()

    def plot_example(self, tr):
        x = np.arange(1, 13)
        this_year = np.array([10, 12, 9, 11, 13, 22, 26, 23, 20, 18, 21, 22]) * 1000 / 1.2
        last_year = np.array([8, 10, 11, 10, 12, 18, 20, 17, 15, 14, 19, 25]) * 1000 / 1.1
        self.ax.clear()
        self.ax.plot(x, this_year, linewidth=2.5, label=tr["data"])
        self.ax.plot(x, last_year, linestyle="--", linewidth=1.8, label=tr["events_created"])
        self.ax.fill_between(x, this_year, alpha=0.06)
        self.ax.legend(frameon=False, loc="upper left", fontsize=9)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.draw()

# Edit
class EditRowDialog(QDialog):
    def __init__(self, sensor, serial, status, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setWindowTitle(self.tr["edit"])
        self.setModal(True)
        self.resize(360, 160)

        form = QFormLayout()
        self.sensor_edit = QLineEdit(sensor)
        self.serial_edit = QLineEdit(serial)
        self.status_edit = QLineEdit(status)

        form.addRow(f"{self.tr['sensor']}:", self.sensor_edit)
        form.addRow(f"{self.tr['serial']}:", self.serial_edit)
        form.addRow(f"{self.tr['status']}:", self.status_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self):
        return self.sensor_edit.text(), self.serial_edit.text(), self.status_edit.text()


# Main
class DashboardPage(QWidget):
    def __init__(self, lang="en", tr=None):
        super().__init__()
        self.lang = lang
        self.tr = tr or {}
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Filtros
        filters = QHBoxLayout()
        filters.setSpacing(12)

        self.search = QLineEdit()
        self.search.setObjectName("SearchBox")
        self.search.setPlaceholderText(self.tr["search_placeholder"])

        self.conn_type = QComboBox()
        self.conn_type.setObjectName("ComboBox")
        self.conn_type.addItems([
            self.tr["select_conn"],
            "WiFi", "Ethernet", "USB"
        ])

        self.sensor_type = QComboBox()
        self.sensor_type.setObjectName("ComboBox")
        self.sensor_type.addItems([
            self.tr["select_sensor"],
            self.tr["temperature"],
            self.tr["pressure"],
            self.tr["viscosity"]
        ])

        self.add_btn = QPushButton(self.tr["add_sensor"])
        self.add_btn.setObjectName("AddButton")

        filters.addWidget(self.search, 2)
        filters.addWidget(self.conn_type, 1)
        filters.addWidget(self.sensor_type, 1)
        filters.addWidget(self.add_btn, 0)

        # Estadisticas
        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.card1 = self.createStatCard(self.tr["data"], "7,265", "+11.01%")
        self.card2 = self.createStatCard(self.tr["sensors_connected"], "3")
        self.card3 = self.createStatCard(self.tr["events_created"], "156", "+15.03%")
        cards.addWidget(self.card1)
        cards.addWidget(self.card2)
        cards.addWidget(self.card3)

        # Grafico
        middle = QHBoxLayout()
        middle.setSpacing(12)

        chart_frame = QFrame()
        chart_frame.setObjectName("ChartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(12, 12, 12, 12)

        self.chart_title = QLabel(self.tr["total_data"])
        self.chart_title.setObjectName("SectionTitle")
        chart_layout.addWidget(self.chart_title)

        self.canvas = MplCanvas(self, width=6, height=2.6, dpi=100)
        self.canvas.plot_example(self.tr)
        chart_layout.addWidget(self.canvas)

        measures = QFrame()
        measures.setObjectName("MeasuresFrame")
        measures_layout = QVBoxLayout(measures)
        measures_layout.setContentsMargins(12, 12, 12, 12)

        self.lbl_visc = QLabel(self.tr["viscosity"])
        self.lbl_temp = QLabel(self.tr["temperature"])
        self.lbl_dens = QLabel(self.tr["density"])
        self.lbl_pres = QLabel(self.tr["pressure"])

        measures_layout.addWidget(self.lbl_visc)
        measures_layout.addWidget(self.lbl_temp)
        measures_layout.addWidget(self.lbl_dens)
        measures_layout.addWidget(self.lbl_pres)

        middle.addWidget(chart_frame, 3)
        middle.addWidget(measures, 1)

        # Tabla
        self.table_title = QLabel(self.tr["sensor_table"])
        self.table_title.setObjectName("SectionTitle")

        self.table = QTableWidget(4, 5)
        self.table.setObjectName("SensorTable")
        self.table.setHorizontalHeaderLabels([
            self.tr["sensor"],
            self.tr["serial"],
            self.tr["status"],
            self.tr["action"],
            self.tr["edit"]
        ])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)

        self.data = [
            ("SRD", "SRD-000-AC00", self.tr["status"], True),
            ("DVM", "DVM-000-GG00", self.tr["status"], False),
            ("SRV", "SRV-000-RT00", self.tr["status"], True),
            ("DVP", "DVP-000-WD00", self.tr["status"], False),
        ]
        self.populate_table()

        layout.addLayout(filters)
        layout.addLayout(cards)
        layout.addLayout(middle)
        layout.addWidget(self.table_title)
        layout.addWidget(self.table)

    # Poblar
    def populate_table(self):
        self.table.setRowCount(len(self.data))
        for row, (sensor, sn, status, active) in enumerate(self.data):
            self.table.setItem(row, 0, QTableWidgetItem(sensor))
            self.table.setItem(row, 1, QTableWidgetItem(sn))
            self.table.setItem(row, 2, QTableWidgetItem(status))
            toggle = ToggleSwitch()
            toggle.setChecked(active)
            toggle.stateChanged.connect(lambda st, r=row: self.on_switch_toggled(r, st))
            self.table.setCellWidget(row, 3, toggle)
            edit_btn = QPushButton()
            edit_btn.setObjectName("EditButton")
            icon_path = os.path.join(BASE, "assets", "edit.png")
            if os.path.exists(icon_path):
                edit_btn.setIcon(QIcon(icon_path))
            edit_btn.setFixedSize(QSize(28, 28))
            edit_btn.clicked.connect(lambda _, r=row: self.open_edit_dialog(r))
            self.table.setCellWidget(row, 4, edit_btn)

    def on_switch_toggled(self, row, state):
        checked = state == Qt.Checked
        sensor, sn, status, _ = self.data[row]
        self.data[row] = (sensor, sn, status, checked)

    def open_edit_dialog(self, row):
        sensor, sn, status, active = self.data[row]
        dlg = EditRowDialog(sensor, sn, status, tr=self.tr, parent=self)
        if dlg.exec() == QDialog.Accepted:
            s, serial, st = dlg.values()
            self.data[row] = (s, serial, st, active)
            self.table.item(row, 0).setText(s)
            self.table.item(row, 1).setText(serial)
            self.table.item(row, 2).setText(st)

    # Tarjetas
    def createStatCard(self, title, value, change=None):
        card = QFrame()
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        title_lbl = QLabel(title, objectName="CardTitle")
        value_lbl = QLabel(value, objectName="CardValue")
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        if change:
            change_lbl = QLabel(change, objectName="CardChange")
            layout.addWidget(change_lbl)
        return card

    # Traducciones
    def update_translations(self, lang, tr):
        self.lang = lang
        self.tr = tr
        # Filtros
        self.search.setPlaceholderText(tr["search_placeholder"])
        self.conn_type.setItemText(0, tr["select_conn"])
        self.sensor_type.setItemText(0, tr["select_sensor"])
        self.sensor_type.setItemText(1, tr["temperature"])
        self.sensor_type.setItemText(2, tr["pressure"])
        self.sensor_type.setItemText(3, tr["viscosity"])
        self.add_btn.setText(tr["add_sensor"])
        # Títulos
        self.chart_title.setText(tr["total_data"])
        self.table_title.setText(tr["sensor_table"])
        # Medidas
        self.lbl_visc.setText(tr["viscosity"])
        self.lbl_temp.setText(tr["temperature"])
        self.lbl_dens.setText(tr["density"])
        self.lbl_pres.setText(tr["pressure"])
        # Tarjetas
        self.card1.layout().itemAt(0).widget().setText(tr["data"])
        self.card2.layout().itemAt(0).widget().setText(tr["sensors_connected"])
        self.card3.layout().itemAt(0).widget().setText(tr["events_created"])
        # Tabla
        self.table.setHorizontalHeaderLabels([
            tr["sensor"],
            tr["serial"],
            tr["status"],
            tr["action"],
            tr["edit"]
        ])
        # Redibujar gráfico
        self.canvas.plot_example(tr)