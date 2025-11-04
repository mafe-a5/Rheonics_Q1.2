import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QPainter, QBrush

# ON/OFF
class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fondo del switch
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#5BC4A2")))  # Verde ON
        else:
            painter.setBrush(QBrush(QColor("#D3D5DA")))  # Gris OFF
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)

        # Círculo interior
        painter.setBrush(QBrush(QColor("white")))
        if self.isChecked():
            painter.drawEllipse(self.width() - 24, 4, 20, 20)
        else:
            painter.drawEllipse(4, 4, 20, 20)


# ---------- Clase principal del dashboard ----------
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # 🔹 Cargar hoja de estilo desde carpeta "styles"
        BASE = os.path.dirname(__file__)
        qss_path = os.path.join(BASE, "styles", "dashboard.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print("⚠️ Archivo dashboard.qss no encontrado en:", qss_path)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # -------------------- Filtros superiores --------------------
        filters = QHBoxLayout()
        filters.setSpacing(12)

        search = QLineEdit()
        search.setObjectName("SearchBox")
        search.setPlaceholderText("Search sensor...")

        conn_type = QComboBox()
        conn_type.setObjectName("ComboBox")
        conn_type.addItems(["Select connection type", "WiFi", "Ethernet", "USB"])

        sensor_type = QComboBox()
        sensor_type.setObjectName("ComboBox")
        sensor_type.addItems(["Select sensor type", "Temperature", "Pressure", "Viscosity"])

        add_btn = QPushButton("Add Sensor +")
        add_btn.setObjectName("AddButton")

        filters.addWidget(search)
        filters.addWidget(conn_type)
        filters.addWidget(sensor_type)
        filters.addWidget(add_btn)

        # -------------------- Tarjetas de estadísticas --------------------
        cards = QHBoxLayout()
        cards.setSpacing(12)

        data_card = self.createStatCard("Data", "7,265", "+11.01%")
        connected_card = self.createStatCard("Sensors connected", "3")
        events_card = self.createStatCard("Events created", "156", "+15.03%")

        cards.addWidget(data_card)
        cards.addWidget(connected_card)
        cards.addWidget(events_card)

        # -------------------- Gráfico + medidas --------------------
        middle = QHBoxLayout()
        middle.setSpacing(12)

        chart = QFrame()
        chart.setObjectName("ChartFrame")
        chart_layout = QVBoxLayout(chart)
        chart_title = QLabel("Total Data from sensors")
        chart_title.setObjectName("SectionTitle")
        chart_layout.addWidget(chart_title)

        measures = QFrame()
        measures.setObjectName("MeasuresFrame")
        measures_layout = QVBoxLayout(measures)
        measures_layout.setContentsMargins(8, 8, 8, 8)
        measures_layout.setSpacing(4)
        measures_layout.addWidget(QLabel("<b>Measurements</b>"))
        measures_layout.addWidget(QLabel("1.02 cP  <font color='#E57373'>Viscosity</font>"))
        measures_layout.addWidget(QLabel("25 °C    <font color='#D6A851'>Temperature</font>"))
        measures_layout.addWidget(QLabel("998 g/cc <font color='#80CFA9'>Density</font>"))
        measures_layout.addWidget(QLabel("1.2 bar  <font color='#B9B3F5'>Pressure</font>"))

        middle.addWidget(chart, 3)
        middle.addWidget(measures, 1)

        # -------------------- Tabla de sensores --------------------
        table_title = QLabel("Sensor overview table")
        table_title.setObjectName("SectionTitle")

        table = QTableWidget(4, 5)
        table.setObjectName("SensorTable")
        table.setHorizontalHeaderLabels(["Sensor", "Serial number", "Status", "Action", "Edit"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)

        data = [
            ("SRD", "SRD-000-AC00", "Logging", True),
            ("DVM", "DVM-000-GG00", "Complete", False),
            ("SRV", "SRV-000-RT00", "Pending", False),
            ("DVP", "DVP-000-WD00", "Logging", False),
        ]

        for row, (sensor, sn, status, active) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(sensor))
            table.setItem(row, 1, QTableWidgetItem(sn))
            table.setItem(row, 2, QTableWidgetItem(status))

            toggle = ToggleSwitch()
            toggle.setChecked(active)
            table.setCellWidget(row, 3, toggle)

            edit_btn = QPushButton()
            edit_btn.setObjectName("EditButton")
            edit_btn.setIcon(QIcon.fromTheme("edit"))
            edit_btn.setFixedSize(QSize(28, 28))
            table.setCellWidget(row, 4, edit_btn)

        # -------------------- Añadir todo al layout --------------------
        layout.addLayout(filters)
        layout.addLayout(cards)
        layout.addLayout(middle)
        layout.addWidget(table_title)
        layout.addWidget(table)

    # ---------- Método auxiliar para tarjetas ----------
    def createStatCard(self, title, value, change=None):
        card = QFrame()
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("CardTitle")

        value_lbl = QLabel(value)
        value_lbl.setObjectName("CardValue")

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)

        if change:
            change_lbl = QLabel(change)
            change_lbl.setObjectName("CardChange")
            layout.addWidget(change_lbl)
        return card