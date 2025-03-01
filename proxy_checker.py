'''DSHELLZ LICENCE 2025'''
import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon

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
        self.setWindowTitle("Proxy Checker")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon("ProxyCheckerApp/src/logo.png"))

        layout = QVBoxLayout()

        self.label = QLabel("Aucun fichier chargé", self)
        layout.addWidget(self.label)

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.load_button = QPushButton("Charger une liste de proxy", self)
        self.load_button.clicked.connect(self.load_proxy_file)
        layout.addWidget(self.load_button)

        self.start_button = QPushButton("Démarrer le test", self)
        self.start_button.clicked.connect(self.start_checking)
        self.start_button.setEnabled(False)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Arrêter le test", self)
        self.stop_button.clicked.connect(self.stop_checking)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

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
        QMainWindow::title {
        background-color: #333333;
        color: #ffffff;
        }
        QMainWindow {
        background-color: #333333;
        color: #ffffff;
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProxyCheckerApp()
    window.show()
    sys.exit(app.exec())
'''DSHELLZ LICENCE 2025'''