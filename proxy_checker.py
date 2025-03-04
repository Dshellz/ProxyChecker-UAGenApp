'''DSHELLZ LICENCE 2025'''
import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QTabWidget, QHBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from fake_useragent import UserAgent
import pyperclip

class ProxyCheckerThread(QThread):
    proxy_tested = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, proxy_list):
        super().__init__()
        self.proxy_list = proxy_list
        self.valid_proxies = []
        self.stop_requested = False

    def run(self):
        for proxy in self.proxy_list:
            if self.stop_requested:
                self.proxy_tested.emit("❌ Test arreté.")
                break
            try:
                res = requests.get("https://ipinfo.io/json",
                                   proxies={"http": proxy, "https": proxy, "socks4": proxy, "socks5": proxy},
                                   timeout=5)
                res.raise_for_status()
                self.valid_proxies.append(proxy)
                self.proxy_tested.emit(f"✅ Proxy valide: {proxy}")
            except requests.RequestException:
                self.proxy_tested.emit(f"❌ Proxy invalide: {proxy}")

        with open("valid_proxies.txt", "w") as f:
            for proxy in self.valid_proxies:
                f.write(proxy + "\n")

        self.finished_signal.emit(len(self.valid_proxies))
    
    def stop(self):
        self.stop_requested = True
        self.quit()

class ProxyCheckerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.proxy_list = []
        self.thread = None
        self.initUI()
        self.apply_dark_theme()

    def initUI(self):
        self.setWindowTitle("Proxy Checker & UA Gen")
        self.setGeometry(100, 100, 700, 600)
        self.setWindowIcon(QIcon("logo.ico"))

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.proxy_checker_tab = QWidget()
        self.proxy_checker_layout = QVBoxLayout()

        self.label = QLabel("Aucun fichier chargé", self)
        self.proxy_checker_layout.addWidget(self.label)

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.proxy_checker_layout.addWidget(self.log_output)

        self.load_button = QPushButton("Charger une liste de proxy", self)
        self.load_button.clicked.connect(self.load_proxy_file)
        self.proxy_checker_layout.addWidget(self.load_button)

        self.start_button = QPushButton("Démarrer le test", self)
        self.start_button.clicked.connect(self.start_checking)
        self.start_button.setEnabled(False)
        self.proxy_checker_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Arrêter le test", self)
        self.stop_button.clicked.connect(self.stop_checking)
        self.stop_button.setEnabled(False)
        self.proxy_checker_layout.addWidget(self.stop_button)

        self.proxy_checker_tab.setLayout(self.proxy_checker_layout)
        self.tabs.addTab(self.proxy_checker_tab, "Proxy Checker")

        self.user_agent_tab = QWidget()
        self.user_agent_layout = QVBoxLayout()

        self.ua_label = QLabel("Générateur de User-Agent", self)
        self.user_agent_layout.addWidget(self.ua_label)

        self.generated_ua = QTextEdit(self)
        self.generated_ua.setReadOnly(True)
        self.user_agent_layout.addWidget(self.generated_ua)

        self.generate_button = QPushButton("Générer un User-Agent", self)
        self.generate_button.clicked.connect(self.generate_user_agent)
        self.user_agent_layout.addWidget(self.generate_button)

        self.copy_button = QPushButton("Copier dans le presse-papiers", self)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.user_agent_layout.addWidget(self.copy_button)

        self.user_agent_tab.setLayout(self.user_agent_layout)
        self.tabs.addTab(self.user_agent_tab, "User-Agent Generator")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def apply_dark_theme(self):
        dark_mode_qss = """
        QWidget {
            background-color: #121212;
            color: #ffffff;
        }
        QTextEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #333333;
        }
        QPushButton {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QLabel {
            color: #ffffff;
        }
        QTabWidget {
            background-color: #121212;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
        }
        QTabBar::tab {
            background-color: #333333;
            padding: 10px;
            border-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: #444444;
        }
        """
        self.setStyleSheet(dark_mode_qss)

    def load_proxy_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier de proxys", "", "Fichiers texte (*.txt)")
        if file_name:
            with open(file_name, 'r') as f:
                self.proxy_list = [p.strip() for p in f.readlines() if p.strip()]

            self.label.setText(f"Fichier chargé : {file_name}")
            self.log_output.append(f"{len(self.proxy_list)} proxys chargés.")
            self.start_button.setEnabled(True)

    def start_checking(self):
        if not self.proxy_list:
            self.log_output.append("⚠️ Aucun proxys à tester !")
            return

        self.log_output.append("🔍 Début du test des proxys...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.thread = ProxyCheckerThread(self.proxy_list)
        self.thread.proxy_tested.connect(self.log_output.append)
        self.thread.finished_signal.connect(self.checking_finished)
        self.thread.start()

    def stop_checking(self):
        if self.thread:
            self.thread.stop()
            self.stop_button.setEnabled(False)
            self.log_output.append("❌ Test arreté.")

    def checking_finished(self, valid_count):
        self.log_output.append(f"✅ Test terminé. {valid_count} proxies valides enregistrés.")
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def generate_user_agent(self):
        ua = UserAgent()
        user_agent = ua.random
        self.generated_ua.setPlainText(user_agent)

    def copy_to_clipboard(self):
        user_agent = self.generated_ua.toPlainText()
        pyperclip.copy(user_agent)
        self.log_output.append(f"User-Agent copié dans le presse-papiers: {user_agent}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.ico"))
    window = ProxyCheckerApp()
    window.show()
    sys.exit(app.exec())

'''DSHELLZ LICENCE 2025'''