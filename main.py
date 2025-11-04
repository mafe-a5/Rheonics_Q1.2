import sys, os, json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMenu
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

BASE = os.path.dirname(__file__)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def themed_icon(light, dark, theme):
    folder = "dark" if theme == "dark" else "light"
    file = dark if theme == "dark" else light
    return QIcon(os.path.join(BASE, "assets", folder, file))

def themed_logo(theme, collapsed):
    if theme == "dark":
        return ("Rheonics_Logo_blue_singleline_white 02.png"
            if collapsed else "Rheonics_Logo_blue_singleline_white 01.png")
    return "Rheonics_Logo_blue_singleline-HQ.png"

# Main
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.theme = "light"
        self.collapsed = False
        self.sensors_expanded = False

        self.tr = {
            "en": load_json(os.path.join(BASE, "i18n", "en.json")),
            "es": load_json(os.path.join(BASE, "i18n", "es.json")),
        }

        self.build_ui()
        self.load_theme()
        self.refresh_ui()

    # UI Construction
    def build_ui(self):
        self.setWindowTitle("Challenge Rheonics")
        self.setMinimumSize(1200, 720)

        layout = QHBoxLayout(self)
        self.sidebar = self.build_sidebar()
        self.content = self.build_content()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content, 1)

    def build_sidebar(self):
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(240)

        self.sb = QVBoxLayout(frame)
        self.sb.setSpacing(6)

        self.logo = QLabel(alignment=Qt.AlignCenter)
        self.update_logo()
        self.sb.addWidget(self.logo)
        self.sb.addSpacing(8)

        self.btn_menu = self.nav_btn("menu.png", "menu_white.png", self.toggle_sidebar)
        self.sb.addWidget(self.btn_menu)

        self.btn_home = self.nav_btn("dash.png", "dash_white.png", self.go_dashboard, "dashboard")
        self.sb.addWidget(self.btn_home)

        self.btn_sensors = self.nav_btn("", "", self.toggle_sensors, "sensors")
        self.sb.addWidget(self.btn_sensors)

        self.sensors_container = QVBoxLayout()
        self.sensors_container.setContentsMargins(40, 0, 0, 0)
        self.sensors_container.setSpacing(4)

        self.btn_sensor_item = self.nav_btn("", "", self.open_sensor_screen)
        self.btn_sensor_item.setText("SRV-4829-AC73")
        self.sensors_container.addWidget(self.btn_sensor_item)
        self.sb.addLayout(self.sensors_container)
        self.toggle_sensors(hide_only=True)

        self.sb.addStretch()
        self.btn_help = self.nav_btn("help.png", "help_white.png", self.open_help, "help")
        self.sb.addWidget(self.btn_help)

        self.btn_account = self.nav_btn("account.png", "account_white.png", self.open_account, "account")
        self.sb.addWidget(self.btn_account)

        self.btn_theme = self.nav_btn("moon.png", "moon_white.png", self.toggle_theme, "theme")
        self.sb.addWidget(self.btn_theme)

        self.btn_lang = self.nav_btn("globe.png", "globe_white.png", self.open_language_menu, "language")
        self.sb.addWidget(self.btn_lang)

        return frame

    def build_content(self):
        from dashboard import DashboardPage
        frame = QFrame()
        layout = QVBoxLayout(frame)
        self.header = QLabel(alignment=Qt.AlignLeft)
        self.header.setObjectName("header")
        layout.addWidget(self.header)

        # Dashboard page
        self.dashboard = DashboardPage(lang=self.lang, tr=self.tr[self.lang])
        layout.addWidget(self.dashboard)
        self.dashboard.hide()
        return frame

    def nav_btn(self, light, dark, callback, text_key=None):
        btn = QPushButton()
        btn._icon_light = light
        btn._icon_dark = dark
        btn._text_key = text_key
        btn._full_text = ""
        btn.clicked.connect(callback)
        btn.setIcon(themed_icon(light, dark, self.theme))
        btn.setIconSize(QSize(22, 22))
        btn.setMinimumHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    # Navigation
    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        self.sidebar.setFixedWidth(60 if self.collapsed else 240)

        for btn in [
            self.btn_home, self.btn_sensors, self.btn_sensor_item,
            self.btn_help, self.btn_account, self.btn_theme, self.btn_lang
        ]:
            if self.collapsed:
                btn.setText("▼" if btn == self.btn_sensors else "")
            else:
                if btn._text_key:
                    btn.setText(self.t(btn._text_key))
                    if btn == self.btn_sensors:
                        arrow = "▲" if self.sensors_expanded else "▼"
                        spaces = "                               "
                        btn.setText(f"{btn._full_text}{spaces}{arrow}")
                elif btn == self.btn_sensor_item:
                    btn.setText("SRV-4829-AC73")

        self.toggle_sensors(hide_only=self.collapsed)
        self.update_logo()

    def toggle_sensors(self, hide_only=False):
        if not hide_only:
            self.sensors_expanded = not self.sensors_expanded

        show = self.sensors_expanded and not self.collapsed
        for i in range(self.sensors_container.count()):
            widget = self.sensors_container.itemAt(i).widget()
            widget.setVisible(show)

        spaces = "                               "
        if not self.collapsed:
            arrow = "▲" if self.sensors_expanded else "▼"
            self.btn_sensors.setText(f"{self.btn_sensors._full_text}{spaces}{arrow}")
        else:
            self.btn_sensors.setText("▼")

    def hide_all_pages(self):
        self.dashboard.hide()

    def go_dashboard(self):
        self.hide_all_pages()
        self.header.setText(self.t("dashboard"))
        self.dashboard.show()

    def open_help(self):
        self.hide_all_pages()
        self.header.setText(self.t("help"))

    def open_account(self):
        self.hide_all_pages()
        self.header.setText(self.t("account"))

    def open_sensor_screen(self):
        self.hide_all_pages()
        self.header.setText("SRV-4829-AC73")

    def open_language_menu(self):
        menu = QMenu()
        menu.setStyleSheet(self.styleSheet())

        flag_en = os.path.join(BASE, "assets", "ingles.png")
        flag_es = os.path.join(BASE, "assets", "español.png")

        a_en = menu.addAction(QIcon(flag_en), "English")
        a_es = menu.addAction(QIcon(flag_es), "Español")

        pos = self.btn_lang.mapToGlobal(self.btn_lang.rect().topRight())
        action = menu.exec_(pos)
        if action == a_en:
            self.lang = "en"
        elif action == a_es:
            self.lang = "es"

        self.refresh_ui()

        # Actualizar dashboard
        if hasattr(self, "dashboard"):
            self.dashboard.update_translations(self.lang, self.tr[self.lang])

    # Theme & Language
    def t(self, key):
        return self.tr[self.lang].get(key, key) if key else ""

    def refresh_ui(self):
        self.header.setText(self.t("dashboard"))
        spaces = "                               "

        for btn in [self.btn_home, self.btn_sensors, self.btn_help, self.btn_account, self.btn_theme, self.btn_lang]:
            if btn._text_key:
                btn._full_text = self.t(btn._text_key)
            else:
                btn._full_text = ""
            if not self.collapsed:
                if btn == self.btn_sensors:
                    arrow = "▲" if self.sensors_expanded else "▼"
                    btn.setText(f"{btn._full_text}{spaces}{arrow}")
                else:
                    btn.setText(btn._full_text)

        self.update_logo()
        self.update_icons()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.load_theme()
        self.refresh_ui()

    def load_theme(self):
        path = os.path.join(BASE, "styles", f"{self.theme}.qss")
        with open(path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    # Visuals
    def update_logo(self):
        file = themed_logo(self.theme, self.collapsed)
        pix = QPixmap(os.path.join(
            BASE, "assets",
            "dark" if self.theme == "dark" else "light",
            file
        )).scaled(
            180 if not self.collapsed else 40,
            50, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.logo.setPixmap(pix)

    def update_icons(self):
        for btn in [
            self.btn_menu, self.btn_home, self.btn_sensors, self.btn_help,
            self.btn_account, self.btn_theme, self.btn_lang, self.btn_sensor_item
        ]:
            btn.setIcon(themed_icon(btn._icon_light, btn._icon_dark, self.theme))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Dashboard()
    w.show()
    sys.exit(app.exec())