import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLabel, 
                             QVBoxLayout, QWidget, QStackedWidget, QFrame)
from PyQt5.QtGui import QMovie, QColor, QPalette
from PyQt5.QtCore import QProcess, Qt

class HighTechFrame(QFrame):
    """A custom frame with a glowing futuristic border"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 20, 40, 150);
                border: 2px solid cyan;
                border-radius: 15px;
            }
        """)

class AegisUltimateGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AEGIS OPTIMUS - BIOMETRIC UNIT")
        self.setGeometry(100, 100, 900, 700)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 10))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.header_label = QLabel(">> SYSTEM INITIALIZING...", self)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("""
            color: cyan; font-family: 'Courier New'; font-size: 18px; font-weight: bold;
            border-bottom: 2px solid cyan; padding-bottom: 10px;
        """)
        main_layout.addWidget(self.header_label)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")
        
        # 0: IDLE PAGE
        self.page_idle = QLabel()
        self.page_idle.setAlignment(Qt.AlignCenter)
        self.movie_idle = QMovie("idle_core.gif") 
        self.page_idle.setMovie(self.movie_idle)
        self.stack.addWidget(self.page_idle)

        # 1: SCAN PAGE
        self.page_scan = QLabel()
        self.page_scan.setAlignment(Qt.AlignCenter)
        self.movie_scan = QMovie("face_scan.gif") 
        self.page_scan.setMovie(self.movie_scan)
        self.stack.addWidget(self.page_scan)

        # 2: LISTEN PAGE
        self.page_listen = QLabel()
        self.page_listen.setAlignment(Qt.AlignCenter)
        self.movie_listen = QMovie("listening.gif") 
        self.page_listen.setMovie(self.movie_listen)
        self.stack.addWidget(self.page_listen)

        core_frame = HighTechFrame()
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.stack)
        core_frame.setLayout(core_layout)
        main_layout.addWidget(core_frame, stretch=2) 

        log_frame = HighTechFrame()
        log_layout = QVBoxLayout()
        
        log_label = QLabel(">> MISSION LOG")
        log_label.setStyleSheet("color: cyan; font-family: Impact; border: none;")
        log_layout.addWidget(log_label)

        self.terminal = QTextEdit(self)
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            background-color: transparent; 
            color: #00FF00; 
            font-family: Consolas; 
            font-size: 14px; 
            border: none;
        """)
        self.terminal.setFixedHeight(150)
        log_layout.addWidget(self.terminal)
        log_frame.setLayout(log_layout)
        main_layout.addWidget(log_frame)

        # --- PROCESS HANDLING ---
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.process_finished) # Added Finish Trigger
        
        # 🔥 STEP 1: Pehle Face Unlock start karo
        self.current_stage = "FACE_SCAN"
        self.set_status("BIOMETRIC SCAN IN PROGRESS...", "cyan")
        self.stack.setCurrentIndex(1) # Scan GIF lagao
        self.movie_scan.start()
        
        self.terminal.append("[SYSTEM] >> Initializing Biometric Camera...")
        self.process.start(sys.executable, ["-u", "face_unlock.py"])

    def set_status(self, text, color="cyan"):
        self.header_label.setText(f">> {text.upper()}")
        self.header_label.setStyleSheet(f"""
            color: {color}; font-family: 'Courier New'; font-size: 18px; font-weight: bold;
            border-bottom: 2px solid {color}; padding-bottom: 10px;
        """)

    def handle_output(self):
        data = self.process.readAllStandardOutput()
        text_block = bytes(data).decode("utf8").strip()
        
        if not text_block: return

        lines = text_block.split('\n')
        
        for text in lines:
            text = text.strip()
            if not text: continue
            lower_text = text.lower()
            
            # Print everything to terminal
            if lower_text.startswith("aegis:"):
                clean_text = text.replace("AEGIS:", "", 1).strip()
                self.terminal.append(f"[AEGIS] >> {clean_text}")
            elif lower_text.startswith("user:"):
                clean_text = text.replace("User:", "", 1).replace("user:", "", 1).strip()
                self.terminal.append(f"[USER]  >> {clean_text}")
            else:
                self.terminal.append(f">> {text}")

            # --- DYNAMIC GUI ANIMATION LOGIC ---
            if self.current_stage == "MAIN_AI":
                if "[sleep mode]" in lower_text:
                    self.set_status("STANDBY MODE - AWAITING WAKE WORD", "gray")
                    self.stack.setCurrentIndex(0) 
                    self.movie_listen.stop()
                    self.movie_idle.start()

                elif "listening..." in lower_text:
                    self.set_status("LISTENING FOR COMMAND...", "yellow")
                    self.stack.setCurrentIndex(2) 
                    self.movie_idle.stop()
                    self.movie_listen.start()

                elif "processing..." in lower_text:
                     self.set_status("PROCESSING DATA...", "orange")

                elif lower_text.startswith("aegis:"):
                    self.set_status("AEGIS SPEAKING", "cyan")
                    self.stack.setCurrentIndex(0) 

        # Scroll terminal to bottom
        cursor = self.terminal.textCursor()
        cursor.movePosition(cursor.End)
        self.terminal.setTextCursor(cursor)

    def process_finished(self, exit_code, exit_status):
        """Ye function tab chalta hai jab koi backend file band hoti hai"""
        if self.current_stage == "FACE_SCAN":
            # Agar Face Unlock script bina error ke band hui hai (matlab face mil gaya)
            if exit_code == 0:
                self.set_status("ACCESS GRANTED - BOOTING MAIN AI...", "green")
                self.movie_scan.stop()
                
                # 🔥 STEP 2: Ab Main.py start karo
                self.current_stage = "MAIN_AI"
                self.process.start(sys.executable, ["-u", "main.py"])
            else:
                self.set_status("ACCESS DENIED - SYSTEM LOCKED", "red")
                self.terminal.append("<span style='color: red;'>[SECURITY] >> Unauthorized User Detected. Stopping.</span>")
                self.movie_scan.stop()

    def handle_error(self):
        data = self.process.readAllStandardError()
        error = bytes(data).decode("utf8")
        if error.strip():
            self.terminal.append(f"<span style='color: red;'>[SYSTEM ERROR] >> {error}</span>")

    def closeEvent(self, event):
        self.process.kill()
        self.process.waitForFinished(1000)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AegisUltimateGUI()
    window.show()
    sys.exit(app.exec_())