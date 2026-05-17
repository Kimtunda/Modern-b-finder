from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QPushButton, QFileDialog,QVBoxLayout,QDialog, QLineEdit
import os
import sys
import keyring
from keyring.errors import NoKeyringError
from xhtml2pdf import pisa
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import qrcode
from io import BytesIO
import subprocess
import importlib
import webbrowser



# --- Custom Dialogs ---
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bfinder Login")
        self.setFixedSize(370, 220)
        self.setStyleSheet("""
            background: #23272e;
            color: #f5f6fa;
            border-radius: 14px;
        """)
        layout = QtWidgets.QVBoxLayout(self)
        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap("images/logo.png").scaled(60, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        logo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo)
        title = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Welcome to <b>Bfinder</b></h2>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(8)
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password (default: 1234)")
        self.password_input.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 8px; background: #181a20; color: #00bf63;")
        layout.addWidget(self.password_input)
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: #ff4d4f; font-size: 14px;")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.error_label)
        btn = QtWidgets.QPushButton("Login")
        btn.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 8px; background: #00bf63; color: white;")
        btn.clicked.connect(self.check_password)
        layout.addWidget(btn)
        self.password_input.returnPressed.connect(self.check_password)
        self.setLayout(layout)
        self.setModal(True)
        self.password_input.setFocus()

    def check_password(self):
        import keyring
        password = self.password_input.text()
        # Try to get password from keyring or fallback
        try:
            correct = keyring.get_password("system", "user")
        except Exception:
            correct = None
        if not correct:
            try:
                with open("system_password.txt", "r", encoding="utf-8") as f:
                    correct = f.read().strip()
            except Exception:
                correct = "1234"
        if password == correct:
            self.accept()
        else:
            self.error_label.setText("Incorrect password. Please try again.")
            self.password_input.clear()
            self.password_input.setFocus()

class WelcomePopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Bfinder!")
        self.setFixedSize(440, 350)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23272e, stop:1 #00bf63);
                border-radius: 18px;
            }
        """)
        # Drop shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(32)
        shadow.setColor(QtGui.QColor(0, 191, 99, 120))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(10)
        # Logo (no animation to avoid geometry errors before show)
        logo = QtWidgets.QLabel()
        try:
            pixmap = QtGui.QPixmap("images/logo.png")
            if pixmap.isNull():
                raise Exception("Logo not found")
            logo.setPixmap(pixmap.scaled(90, 90, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        except Exception:
            logo.setText("<b>Bfinder</b>")
            logo.setStyleSheet("font-size: 32px; color: #00bf63;")
        logo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo)
        # Title
        title = QtWidgets.QLabel("<h2 style='color:#00bf63; letter-spacing:1px;'>Welcome to Bfinder</h2>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        # Subtitle (no <img> tag)
        subtitle = QtWidgets.QLabel("<span style='font-size:16px;color:#f5f6fa;'>Your modern bug & vulnerability finder</span>")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle)
        # Info box (plain text, no <ul>, <li>, <div>)
        info_text = (
            "<span style='font-size:15px;color:#23272e;background:#e0e0e0;border-radius:12px;padding:16px 18px 12px 18px;display:block;'>"
            "• Scan your code and websites for vulnerabilities<br>"
            "• Generate secure, actionable reports<br>"
            "• Customize your experience in Settings<br>"
            "• Earn badges for bug hunting!<br><br>"
            "<span style='font-size:14px;color:#00bf63;'>Default password: <b>1234</b> <span style='color:#23272e;'>(change it in Settings)</span></span>"
            "</span>"
        )
        info = QtWidgets.QLabel(info_text)
        info.setAlignment(QtCore.Qt.AlignLeft)
        info.setWordWrap(True)
        info.setStyleSheet("background: #e0e0e0; border-radius: 12px; padding: 16px 18px 12px 18px; margin-top: 8px;")
        layout.addWidget(info)
        layout.addStretch()
        # Get Started button
        ok_btn = QtWidgets.QPushButton("Get Started →")
        ok_btn.setStyleSheet("""
            QPushButton {
                padding: 14px 32px; font-size: 18px; border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bf63, stop:1 #007bff);
                color: white; font-weight: bold; letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007bff, stop:1 #00bf63);
                color: #fff;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(layout)
        self.show()
        ok_btn.setFocus()
        self.exec_()

class ModernMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_info = self.load_user_info()
        self.setWindowTitle("Bfinder - Modern Edition")
        self.setWindowIcon(QtGui.QIcon("images/icon.png"))
        self.setMinimumSize(1000, 650)
        self.setStyleSheet("background: #23272e; color: #f5f6fa; font-family: 'Segoe UI', 'Cantarell', 'Arial', sans-serif; font-size: 16px;")
        self.font_family = 'Segoe UI'
        self.font_size = 16
        self.is_dark_theme = True
        self.theme_preference = 'dark'
        self.setup_analytics()

        # Top bar
        self.top_bar = QtWidgets.QWidget()
        self.top_bar.setStyleSheet("background: #181a20; height: 60px; border-bottom: 1px solid #00bf63;")
        self.top_layout = QtWidgets.QHBoxLayout(self.top_bar)
        self.logo = QtWidgets.QLabel()
        self.logo.setPixmap(QtGui.QPixmap("images/logo.png"))
        self.logo.setFixedSize(48, 48)
        self.logo.setScaledContents(True)
        self.title = QtWidgets.QLabel("Bfinder")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00bf63; letter-spacing: 2px;")
        self.top_layout.addWidget(self.logo)
        self.top_layout.addWidget(self.title)
        self.top_layout.addStretch()
        self.user_label = QtWidgets.QLabel("Welcome, User")
        self.user_label.setStyleSheet("font-size: 16px; color: #f5f6fa;")
        self.top_layout.addWidget(self.user_label)
        self.top_bar.setLayout(self.top_layout)

        # Sidebar
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setStyleSheet("background: #181a20; border-right: 1px solid #00bf63;")
        self.sidebar.setFixedWidth(180)
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 30, 0, 0)
        self.sidebar_layout.setSpacing(18)
        def make_sidebar_btn(text, icon=None):
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet("padding: 14px; font-size: 17px; border-radius: 10px; background: #23272e; color: #00bf63; font-weight: 600;")
            if icon:
                btn.setIcon(QtGui.QIcon(icon))
                btn.setIconSize(QtCore.QSize(24, 24))
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            return btn
        # Sidebar buttons as instance variables for language/font updates
        self.btn_dashboard = make_sidebar_btn("Dashboard", "images/ba.png")
        self.btn_home = make_sidebar_btn("Home", "images/bapp.png")
        self.btn_bug = make_sidebar_btn("Bug Report", "images/change.png")
        self.btn_tips = make_sidebar_btn("Security Tips", "images/pro.png")
        self.btn_doc = make_sidebar_btn("Documentation", "images/doc.png")
        self.btn_settings = make_sidebar_btn("Settings", "images/icon.png")
        self.btn_analytics = make_sidebar_btn("Analytics", "images/ba.png")
        self.btn_report_bug = make_sidebar_btn("Report a Bug", "images/con.png")
        self.sidebar_layout.insertWidget(0, self.btn_dashboard)
        self.sidebar_layout.addWidget(self.btn_home)
        self.sidebar_layout.addWidget(self.btn_bug)
        self.sidebar_layout.addWidget(self.btn_tips)
        self.sidebar_layout.addWidget(self.btn_doc)
        self.sidebar_layout.addWidget(self.btn_settings)
        self.sidebar_layout.insertWidget(5, self.btn_analytics)
        self.sidebar_layout.insertWidget(6, self.btn_report_bug)
        self.sidebar_layout.addStretch()
        self.btn_report_bug.clicked.connect(self.open_bug_report_dialog)

        # Sidebar highlight
        self.sidebar_highlight = QtWidgets.QFrame(self.sidebar)
        self.sidebar_highlight.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bf63, stop:1 #23272e); border-radius: 8px;"
        )
        self.sidebar_highlight.setGeometry(5, 0, 170, 48)
        self.sidebar_highlight.lower()
        self.sidebar_anim = QtCore.QPropertyAnimation(self.sidebar_highlight, b"geometry")
        self.sidebar_anim.setDuration(300)
        self.sidebar_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        # Central stacked widget
        self.stacked_widget = QtWidgets.QStackedWidget()

        # Home Page (Redesigned)
        self.page_home = QtWidgets.QWidget()
        home_layout = QtWidgets.QVBoxLayout(self.page_home)
        home_layout.setContentsMargins(40, 30, 40, 30)
        home_layout.setSpacing(24)

        # Remove the previous image/user card above the welcome message and add the new image
        hero_img_label = QtWidgets.QLabel()
        hero_img = QtGui.QPixmap("images/83633cb6-4a0a-421b-9b28-0badae055de4.png")
        hero_img_label.setPixmap(hero_img)
        hero_img_label.setScaledContents(True)
        hero_img_label.setMinimumHeight(220)
        hero_img_label.setMaximumHeight(320)
        hero_img_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        hero_img_label.setStyleSheet("border-radius: 18px; margin-bottom: 18px;")
        home_layout.addWidget(hero_img_label)

        # Welcome/hero message (centered, visually separated)
        home_label = QtWidgets.QLabel("""
        <h2 style='color:#00bf63; margin-top:18px;'>Welcome to <b>Bfinder!</b></h2>
        <p style='font-size:18px; color:#f5f6fa; margin-bottom:10px;'>
        Your modern bug and vulnerability finder for web projects.<br>
        Scan, analyze, and secure your code with ease.
        </p>
        """)
        home_label.setAlignment(QtCore.Qt.AlignCenter)
        home_label.setStyleSheet("font-size: 18px; color: #f5f6fa; margin-top: 10px; margin-bottom: 10px;")
        home_layout.addWidget(home_label)

        # Get Started button (centered, with spacing)
        get_started_btn = QtWidgets.QPushButton("Get Started: Scan Project")
        get_started_btn.setStyleSheet(
            "padding: 14px 32px; font-size: 18px; border-radius: 10px; background: #00bf63; color: white; font-weight: 600; margin-top: 12px;"
        )
        get_started_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        get_started_btn.clicked.connect(self.browse_directory)
        home_layout.addWidget(get_started_btn, alignment=QtCore.Qt.AlignCenter)

        # Quick insights area (centered, below button)
        self.insights_label = QtWidgets.QLabel()
        self.insights_label.setAlignment(QtCore.Qt.AlignCenter)
        self.insights_label.setStyleSheet("font-size: 16px; color: #00bf63; margin-top: 18px;")
        home_layout.addWidget(self.insights_label)

        self.update_home_insights()
        self.user_info = self.load_user_info()

        # Gamification: badges/achievements
        self.badges = self.user_info.get('badges', [])
        self.scan_count = self.user_info.get('scan_count', 0)
        self.bug_count = self.user_info.get('bug_count', 0)

        # Bug Report Page
        self.page_bug = QtWidgets.QWidget()
        bug_layout = QtWidgets.QVBoxLayout(self.page_bug)
        bug_layout.setContentsMargins(40, 30, 40, 30)
        bug_layout.setSpacing(18)
        self.bug_list_widget = QtWidgets.QListWidget()
        self.bug_list_widget.setStyleSheet("background: #23272e; border: 1px solid #00bf63; border-radius: 8px; color: #f5f6fa; font-size: 16px;")
        bug_layout.addWidget(self.bug_list_widget)
        self.bug_browse_btn = QPushButton("Browse Directory for Bugs")
        self.bug_browse_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        self.bug_browse_btn.clicked.connect(self.browse_directory)
        bug_layout.addWidget(self.bug_browse_btn)
        self.bug_scan_website_btn = QPushButton("Scan Website for Bugs")
        self.bug_scan_website_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        self.bug_scan_website_btn.clicked.connect(self.scan_website_dialog)
        bug_layout.addWidget(self.bug_scan_website_btn)
        self.print_report_btn = QPushButton("Print Bug Report")
        self.print_report_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        self.print_report_btn.clicked.connect(self.print_report)
        bug_layout.addWidget(self.print_report_btn)
        self.export_qr_btn = QPushButton("Export Bug Report as QR")
        self.export_qr_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        self.export_qr_btn.clicked.connect(self.export_bug_report_qr)
        bug_layout.addWidget(self.export_qr_btn)
        # Security Tips Page
        self.page_tips = QtWidgets.QWidget()
        tips_layout = QtWidgets.QVBoxLayout(self.page_tips)
        tips_layout.setContentsMargins(40, 30, 40, 30)
        tips_layout.setSpacing(18)
        tips_label = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Security Tips</h2>")
        tips_label.setAlignment(QtCore.Qt.AlignCenter)
        tips_label.setStyleSheet("font-size: 22px; color: #00bf63; font-weight: bold;")
        tips_layout.addWidget(tips_label)
        # Redesigned tips content with modern accent and clean style
        tips_content = [
            ("images/change.png", "Keep your software updated to protect against vulnerabilities."),
            ("images/lock.png", "Use strong, unique passwords for different accounts."),
            ("images/key.png", "Enable two-factor authentication (2FA) where possible."),
            ("images/warning.png", "Be cautious of phishing attempts and suspicious links."),
            ("images/backup.png", "Regularly back up your data to recover from potential loss.")
        ]
        for idx, (icon_path, tip) in enumerate(tips_content):
            tip_widget = QtWidgets.QWidget()
            tip_layout = QtWidgets.QHBoxLayout(tip_widget)
            tip_layout.setContentsMargins(0, 0, 0, 0)
            tip_layout.setSpacing(12)
            icon_label = QtWidgets.QLabel()
            # Only show icon if it exists and not for the first tip
            if idx != 0 and os.path.exists(icon_path):
                icon_label.setPixmap(QtGui.QPixmap(icon_path).scaled(28, 28, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                tip_layout.addWidget(icon_label)
            tip_text = QtWidgets.QLabel(tip)
            tip_text.setWordWrap(True)
            tip_text.setStyleSheet("font-size: 16px; color: #23272e; font-family: 'Segoe UI', Arial, sans-serif;")
            tip_widget.setStyleSheet(
                "background: #e0f7ef; border-left: 6px solid #00bf63; border-radius: 10px; padding: 12px 18px; margin-bottom: 4px;"
            )
            tip_layout.addWidget(tip_text)
            tip_layout.addStretch()
            tips_layout.addWidget(tip_widget)
        # Settings Page
        self.page_settings = QtWidgets.QWidget()
        settings_layout = QtWidgets.QVBoxLayout(self.page_settings)
        settings_layout.setContentsMargins(40, 30, 40, 30)
        settings_layout.setSpacing(18)
        settings_label = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Settings</h2>")
        settings_label.setAlignment(QtCore.Qt.AlignCenter)
        settings_label.setStyleSheet("font-size: 22px; color: #f5f6fa;")
        settings_layout.addWidget(settings_label)

        # Language selection
        lang_row = QtWidgets.QHBoxLayout()
        lang_label = QtWidgets.QLabel("Language:")
        lang_label.setStyleSheet("font-size: 16px;")
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(["English", "Spanish", "French", "German"])
        self.lang_combo.setCurrentText("English")
        self.lang_combo.setStyleSheet("font-size: 15px; background: #23272e; color: #00bf63; border-radius: 6px;")
        lang_row.addWidget(lang_label)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        settings_layout.addLayout(lang_row)
        # Connect language combo box signal
        self.lang_combo.currentTextChanged.connect(self.change_language)

        # Font style (family) selection
        font_row = QtWidgets.QHBoxLayout()
        font_label = QtWidgets.QLabel("Font Style:")
        font_label.setStyleSheet("font-size: 16px;")
        self.font_combo = QtWidgets.QFontComboBox()
        self.font_combo.setCurrentFont(QtGui.QFont(self.font_family))
        self.font_combo.setStyleSheet("font-size: 15px; background: #23272e; color: #00bf63; border-radius: 6px;")
        font_row.addWidget(font_label)
        font_row.addWidget(self.font_combo)
        font_row.addStretch()
        settings_layout.addLayout(font_row)
        # Connect font combo box signal
        self.font_combo.currentFontChanged.connect(self.change_font_family)

        # Font size adjustment
        size_row = QtWidgets.QHBoxLayout()
        font_size_label = QtWidgets.QLabel("Font Size:")
        font_size_label.setStyleSheet("font-size: 16px;")
        self.font_size_spin = QtWidgets.QSpinBox()
        self.font_size_spin.setRange(10, 30)
        self.font_size_spin.setValue(self.font_size)
        self.font_size_spin.setStyleSheet("font-size: 15px; background: #23272e; color: #00bf63; border-radius: 6px;")
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        size_row.addWidget(font_size_label)
        size_row.addWidget(self.font_size_spin)
        size_row.addStretch()
        settings_layout.addLayout(size_row)

        # Theme switch (only in Settings)
        theme_row = QtWidgets.QHBoxLayout()
        theme_label = QtWidgets.QLabel("Theme:")
        theme_label.setStyleSheet("font-size: 16px;")
        self.theme_switch = QtWidgets.QPushButton("Switch to Light Theme")
        self.theme_switch.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        self.theme_switch.setCheckable(True)
        self.theme_switch.toggled.connect(self.toggle_theme)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_switch)
        theme_row.addStretch()
        settings_layout.addLayout(theme_row)

        # Password change section
        pass_row = QtWidgets.QHBoxLayout()
        password_label = QtWidgets.QLabel("Change Password:")
        password_label.setStyleSheet("font-size: 16px;")
        self.change_password_btn = QtWidgets.QPushButton("Change Password")
        self.change_password_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        self.change_password_btn.clicked.connect(self.change_password_dialog)
        pass_row.addWidget(password_label)
        pass_row.addWidget(self.change_password_btn)
        pass_row.addStretch()
        settings_layout.addLayout(pass_row)
        settings_layout.addStretch()

        # Analytics Page
        self.page_analytics = QtWidgets.QWidget()
        analytics_layout = QtWidgets.QVBoxLayout(self.page_analytics)
        analytics_layout.setContentsMargins(40, 30, 40, 30)
        analytics_layout.setSpacing(18)
        self.analytics_label = QtWidgets.QLabel()
        self.analytics_label.setAlignment(QtCore.Qt.AlignCenter)
        self.analytics_label.setStyleSheet("font-size: 22px; color: #00bf63;")
        analytics_layout.addWidget(self.analytics_label)
        analytics_title = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Analytics</h2>")
        analytics_title.setAlignment(QtCore.Qt.AlignCenter)
        analytics_title.setStyleSheet("font-size: 22px; color: #f5f6fa;")
        analytics_layout.addWidget(analytics_title)
        analytics_layout.addStretch()

        # Documentation Page
        self.page_doc = QtWidgets.QWidget()
        doc_layout = QtWidgets.QVBoxLayout(self.page_doc)
        doc_layout.setContentsMargins(40, 30, 40, 30)
        doc_layout.setSpacing(18)
        doc_label = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Documentation</h2>")
        doc_label.setAlignment(QtCore.Qt.AlignCenter)
        doc_label.setStyleSheet("font-size: 22px; color: #f5f6fa;")
        doc_layout.addWidget(doc_label)
        doc_content = [
            "Welcome to the Bfinder documentation!",
            "Bfinder is a modern bug and vulnerability finder for web projects. It helps you scan, analyze, and secure your code with ease.",
            "",
            "<b>Features:</b>",
            "- Scan local directories and website URLs for common vulnerabilities.",
            "- Generate PDF and QR code reports.",
            "- Integrate with CI/CD pipelines for automated security checks.",
            "- View analytics and live dashboards.",
            "- Customize scanning rules and settings.",
            # Removed: "- Gamification: Earn badges for scanning and bug hunting.",
            "",
            "<b>How to use:</b>",
            "1. Use the sidebar to navigate between Home, Bug Report, Security Tips, Analytics, and Settings.",
            "2. On the Bug Report page, click 'Browse Directory for Bugs' or 'Scan Website for Bugs' to start scanning.",
            "3. Review detected bugs and vulnerabilities in the list.",
            "4. Generate reports or export results as QR codes.",
            "5. Adjust your preferences in the Settings tab.",
            "",
            "<b>Security Tips:</b> Visit the Security Tips tab for best practices.",
            "",
            # Removed: "<b>CI/CD Integration:</b> See the CI/CD Integration tab for setup instructions.",
            "",
            "<b>Default password:</b> 1234 (change it in Settings!)",
            "",
            "For more help, see the README or contact support."
        ]
        # Remove CI/CD Integration Page creation and references
        doc_content = [line for line in doc_content if "CI/CD" not in line and "Gamification" not in line]
        doc_content_label = QtWidgets.QLabel(
            "<br>".join([f"<span style='font-size:16px;color:#f5f6fa'>{line}</span>" for line in doc_content])
        )
        doc_content_label.setAlignment(QtCore.Qt.AlignCenter)
        doc_content_label.setWordWrap(True)
        doc_layout.addWidget(doc_content_label, alignment=QtCore.Qt.AlignCenter)
        doc_layout.addStretch()

        # Dashboard Page (ensure dashboard_label is set for theme switching)
        self.page_dashboard = QtWidgets.QWidget()
        dashboard_layout = QtWidgets.QVBoxLayout(self.page_dashboard)
        dashboard_layout.setContentsMargins(40, 30, 40, 30)
        dashboard_layout.setSpacing(18)
        self.dashboard_label = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Dashboard</h2>")
        self.dashboard_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dashboard_label.setStyleSheet("font-size: 22px; color: #00bf63;")
        dashboard_layout.addWidget(self.dashboard_label)
        self.dashboard_canvas = FigureCanvas(Figure())
        self.dashboard_ax = self.dashboard_canvas.figure.add_subplot(111)
        self.dashboard_ax.set_title('Bug Type Distribution', color='#00bf63', fontsize=16)
        dashboard_layout.addWidget(self.dashboard_canvas)
        self.dashboard_legend = QtWidgets.QLabel()
        self.dashboard_legend.setAlignment(QtCore.Qt.AlignCenter)
        self.dashboard_legend.setStyleSheet("font-size: 15px; color: #f5f6fa; margin-top: 10px;")
        dashboard_layout.addWidget(self.dashboard_legend)
        dashboard_layout.addStretch()

        # Threat Intel Page (ensure threat_label is set for theme switching)
        self.page_threat = QtWidgets.QWidget()
        threat_layout = QtWidgets.QVBoxLayout(self.page_threat)
        threat_layout.setContentsMargins(40, 30, 40, 30)
        threat_layout.setSpacing(18)
        self.threat_label = QtWidgets.QLabel("<h2 style='color:#00bf63;'>Threat Intelligence</h2>")
        self.threat_label.setAlignment(QtCore.Qt.AlignCenter)
        self.threat_label.setStyleSheet("font-size: 22px; color: #f5f6fa;")
        threat_layout.addWidget(self.threat_label)
        self.threat_list = QtWidgets.QListWidget()
        self.threat_list.setStyleSheet("background: #23272e; border: 1px solid #00bf63; border-radius: 8px; color: #f5f6fa; font-size: 16px;")
        threat_layout.addWidget(self.threat_list)
        threat_layout.addStretch()

        # Add all pages to stacked widget (ensure all pages are defined above this)
        self.stacked_widget.addWidget(self.page_home)
        self.stacked_widget.addWidget(self.page_bug)
        self.stacked_widget.addWidget(self.page_tips)
        self.stacked_widget.addWidget(self.page_doc)
        self.stacked_widget.addWidget(self.page_settings)
        self.stacked_widget.addWidget(self.page_analytics)
        self.stacked_widget.addWidget(self.page_dashboard)
        # self.stacked_widget.addWidget(self.page_threat)
        # self.stacked_widget.addWidget(self.page_cicd)

        # Sidebar navigation and highlight
        sidebar_buttons = [
            self.btn_dashboard, self.btn_home, self.btn_bug, self.btn_tips, self.btn_doc, self.btn_settings,
            self.btn_analytics, self.btn_report_bug
        ]
        page_widgets = [
            self.page_dashboard, self.page_home, self.page_bug, self.page_tips, self.page_doc, self.page_settings,
            self.page_analytics, None  # btn_report_bug (None)
        ]
        for i, btn in enumerate(sidebar_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.animate_sidebar_highlight(idx))
            if i < len(page_widgets) and page_widgets[i] is not None:
                if btn == self.btn_analytics:
                    btn.clicked.connect(lambda checked: self.show_analytics())
                else:
                    btn.clicked.connect(lambda checked, idx=i: self.stacked_widget.setCurrentWidget(page_widgets[idx]))
        # Remove this redundant connection:
        # elif btn == self.btn_report_bug:
        #     btn.clicked.connect(self.open_bug_report_dialog)

        # Set initial page
        self.stacked_widget.setCurrentWidget(self.page_home)

        # Main layout (top bar + sidebar + stacked widget)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.top_bar)
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(content_layout)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Show login dialog before welcome popup or main window
        if not self.show_login_dialog():
            sys.exit(0)
        # Show welcome popup only on first run
        if not os.path.exists('user_profile.json'):
            try:
                self.show_welcome_popup()
            except Exception as e:
                print("Failed to show welcome popup:", e)

        # Initialize bug report data
        self.bug_report_data = []

    def print_report(self):
        if self.bug_report_data:
            from functions.bug_exp import get_bug_explanation
            from xhtml2pdf import pisa
            import tempfile
            import matplotlib.pyplot as plt
            bug_report = self.bug_report_data
            directory_path = os.path.dirname(bug_report[0][1]) if bug_report else "Unknown"
            directory_name = os.path.basename(directory_path)
            output_pdf = f"{directory_name}_report.pdf"
            header_html = '''
             <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <img src="images/pro.png" width="70" height="70" style="margin-right: 18px;"/>
                <span style="font-size: 26px; color: #00bf63; font-weight: bold;">Bfinder Bug Report</span>
             </div>
            '''
            # Save dashboard chart as image with legend and title
            chart_img_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_chart:
                    chart_img_path = tmp_chart.name
                # Draw chart with legend and title for the PDF
                fig, ax = plt.subplots(figsize=(6, 4))
                from collections import Counter
                bug_types = [b[0] for b in bug_report if len(b) > 0]
                counts = Counter(bug_types)
                labels = list(counts.keys())
                sizes = list(counts.values())
                colors = ['#00bf63', '#007bff', '#ff4d4f', '#f5f6fa', '#23272e', '#e0e0e0']
                wedges, texts, autotexts = ax.pie(
                    sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)],
                    textprops={'color': '#23272e', 'fontsize': 10}
                )
                ax.set_title('Bug Type Distribution', color='#00bf63', fontsize=14)
                ax.legend(wedges, labels, title="Bug Types", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
                plt.tight_layout()
                plt.savefig(chart_img_path, bbox_inches='tight', dpi=120)
                plt.close(fig)
            except Exception:
                chart_img_path = None
            # Chart description
            chart_desc = "<div style='font-size:14px; color:#23272e; margin: 8px 0 18px 0;'><b>Bug Type Distribution:</b> The chart above shows the proportion of each bug type found in the scanned project. Each color represents a different bug type, as shown in the legend.</div>"
            # Table styling for better fitting and no overlap
            def wrap_text(text, width=50):
                import textwrap
                return '<br>'.join(textwrap.wrap(str(text), width=width))
            table_html = """
            <table style=\"border-collapse: collapse; width: 100%; border: 1px solid #00bf63; font-size: 10px;\">
                <tr style=\"background-color: #00bf63; color: #fff; text-align: center; font-weight: bold;\">
                    <th style=\"padding:6px; width: 15%;\">Bug Type</th>
                    <th style=\"padding:6px; width: 30%;\">File/URL</th>
                    <th style=\"padding:6px; width: 55%;\">Mitigation</th>
                </tr>
            """
            for bug in bug_report:
                bug_type, file_path = bug[:2]
                explanation = bug[2] if len(bug) > 2 and bug[2] else get_bug_explanation(bug_type)
                if not explanation or 'No explanation available' in explanation or explanation.lower().startswith('refer'):
                    explanation = self.get_mitigation_measures(bug_type, fallback_only=False)
                table_html += f"""
                <tr>
                    <td style=\"padding: 6px; vertical-align: top;\">{wrap_text(bug_type, 30)}</td>
                    <td style=\"padding: 6px; vertical-align: top;\">{wrap_text(file_path, 40)}</td>
                    <td style=\"padding: 6px; vertical-align: top;\">{wrap_text(explanation, 50)}</td>
                </tr>
                """
            table_html += "</table>"
            # Embed chart image if available
            chart_html = ""
            if chart_img_path and os.path.exists(chart_img_path):
                chart_html = f'<div style="margin: 18px 0 10px 0;"><img src="{chart_img_path}" width="480" style="border: 1px solid #00bf63; border-radius: 8px;"/></div>'
            html_content = f'<div>{header_html}</div>{chart_html}{chart_desc}<div>{table_html}</div>'
            with open(output_pdf, "wb") as pdf_file:
                pisa.CreatePDF(html_content, dest=pdf_file)
            # Robust password retrieval for encryption
            try:
                system_password = keyring.get_password("system", "user")
            except Exception:
                try:
                    with open("system_password.txt", "r", encoding="utf-8") as f:
                        system_password = f.read().strip()
                except Exception:
                    system_password = "1234"
            if not system_password:
                system_password = "1234"
            # Encrypt PDF
            try:
                PyPDF2 = importlib.import_module('PyPDF2')
                with open(output_pdf, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_writer = PyPDF2.PdfWriter()
                    for page_num in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    pdf_writer.encrypt(system_password)
                    with open(output_pdf, 'wb') as encrypted_pdf:
                        pdf_writer.write(encrypted_pdf)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "PDF Encryption Error", f"PDF was generated but could not be encrypted: {e}")
            else:
                QtWidgets.QMessageBox.information(self, "Report", "Report printed and encrypted successfully!")
                try:
                    webbrowser.open_new(output_pdf)
                except Exception:
                    pass
        else:
            QtWidgets.QMessageBox.warning(self, "No report", "No bug report data available.")

    def browse_directory(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "", QFileDialog.ShowDirsOnly)
        if directory_path:
            self.bug_report_data = self.scan_directory(directory_path)
            self.display_bug_report(self.bug_report_data)
            self.update_analytics(self.bug_report_data)
            self.update_dashboard()  # Update chart after scan
            self.show_analytics() # Optionally auto-show analytics after scan

    def setup_analytics(self):
        self.analytics = {
            'scans': 0,
            'bugs_found': 0,
            'last_scan': 'Never'
        }

    def update_analytics(self, bug_report):
        self.analytics['scans'] += 1
        self.analytics['bugs_found'] += len(bug_report) if bug_report else 0
        from datetime import datetime
        self.analytics['last_scan'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.update_home_insights()

    def update_home_insights(self):
        stats = getattr(self, 'analytics', {'scans': 0, 'bugs_found': 0, 'last_scan': 'Never'})
        if hasattr(self, 'insights_label'):
            self.insights_label.setText(f"<b>Scans:</b> {stats['scans']} &nbsp; | &nbsp; <b>Bugs Found:</b> {stats['bugs_found']} &nbsp; | &nbsp; <b>Last Scan:</b> {stats['last_scan']}")

    def show_analytics(self):
        self.stacked_widget.setCurrentWidget(self.page_analytics)
        stats = self.analytics
        self.analytics_label.setText(f"""
            <h2>Analytics Dashboard</h2>
            <p><b>Total Scans:</b> {stats['scans']}<br>
            <b>Bugs Found:</b> {stats['bugs_found']}<br>
            <b>Last Scan:</b> {stats['last_scan']}</p>
        """)

    def open_bug_report_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Report a Bug / Feedback")
        dialog.setFixedSize(400, 250)
        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("Describe the bug or feedback:")
        textedit = QtWidgets.QTextEdit()
        textedit.setPlaceholderText("Please describe the issue or feedback in detail...")
        textedit.setToolTip("Enter your bug report or feedback here.")
        email_label = QtWidgets.QLabel("Your Email (optional):")
        email_input = QtWidgets.QLineEdit()
        email_input.setPlaceholderText("example@email.com")
        email_input.setToolTip("Enter your email if you'd like a response (optional)")
        submit_btn = QtWidgets.QPushButton("Submit")
        submit_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        submit_btn.setToolTip("Submit your bug report or feedback")
        layout.addWidget(label)
        layout.addWidget(textedit)
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        layout.addWidget(submit_btn)
        dialog.setLayout(layout)
        textedit.setFocus()

        def handle_submit():
            report = textedit.toPlainText().strip()
            email = email_input.text().strip()
            if not report:
                QtWidgets.QMessageBox.warning(dialog, "Error", "Bug report/feedback cannot be empty.")
                return
            with open("bug_reports.txt", "a", encoding="utf-8") as f:
                f.write(f"Email: {email}\nReport: {report}\n{'-'*40}\n")
            QtWidgets.QMessageBox.information(dialog, "Thank you!", "Your bug report/feedback has been submitted.")
            textedit.clear()
            email_input.clear()
            dialog.accept()

        submit_btn.clicked.connect(handle_submit)
        dialog.exec_()

    def scan_website_dialog(self):
        sample_urls = [
            "https://example.com",
            "https://httpbin.org/forms/post",
            "https://demo.testfire.net",
            "https://juice-shop.herokuapp.com",
            "https://www.w3schools.com/html/html_forms.asp",
            "https://www.vulnweb.com/",
            "https://testphp.vulnweb.com/",
            "https://xss-game.appspot.com/",
            "https://www.hackthissite.org/",
            "https://www.webscantest.com/",
            "https://bodgeit.herokuapp.com/",  # Intentionally vulnerable
            "https://zero.webappsecurity.com/", # Demo banking app
            "https://www.acunetix.com/vulnerabilities/demo/", # Demo
            "https://www.demoblaze.com/", # E-commerce demo
            "https://www.google.com/", # Safe
            "https://www.wikipedia.org/", # Safe
            "https://testasp.vulnweb.com/", # More vulnweb
            "https://www.owasp.org/index.php/DVWA", # OWASP DVWA
            "https://www.webgoat.net/", # OWASP WebGoat
        ]
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Scan Website")
        dialog.setFixedSize(420, 180)
        layout = QtWidgets.QVBoxLayout(dialog)
        url_input = QtWidgets.QLineEdit()
        url_input.setPlaceholderText("Enter website URL (e.g. https://example.com)")
        url_input.setMinimumWidth(350)
        url_input.setText(sample_urls[0])
        sample_combo = QtWidgets.QComboBox()
        sample_combo.addItems(["(Choose sample URL)"] + sample_urls)
        def set_sample_url(idx):
            if idx > 0:
                url_input.setText(sample_urls[idx-1])
        sample_combo.currentIndexChanged.connect(set_sample_url)
        scan_btn = QtWidgets.QPushButton("Scan")
        scan_btn.setStyleSheet("padding: 10px; font-size: 15px; border-radius: 8px; background: #00bf63; color: white;")
        layout.addWidget(QtWidgets.QLabel("Website URL:"))
        layout.addWidget(url_input)
        layout.addWidget(sample_combo)
        layout.addWidget(scan_btn)
        dialog.setLayout(layout)
        def do_scan():
            url = url_input.text().strip()
            if url:
                self.bug_report_data = self.scan_website_for_vulns(url)
                self.display_bug_report(self.bug_report_data)
                self.update_analytics(self.bug_report_data)
                self.show_analytics()
                dialog.accept()
        scan_btn.clicked.connect(do_scan)
        dialog.exec_()

    def scan_website_for_vulns(self, url):
        """
        Scan a website for common vulnerabilities (simple static checks).
        Returns a list of (bug_type, url, explanation/mitigation) tuples.
        """
        import requests
        from functions.bug_exp import get_bug_explanation
        bug_report = []
        try:
            resp = requests.get(url, timeout=10)
            content = resp.text
            # XSS check
            if '<script>' in content or 'onerror=' in content:
                bug_report.append((
                    'XSS', url,
                    get_bug_explanation('XSS') or self.get_mitigation_measures('XSS')
                ))
            # SQL Injection check (very basic)
            if 'sql' in content.lower() or 'syntax error' in content.lower():
                bug_report.append((
                    'SQL Injection', url,
                    get_bug_explanation('SQL Injection') or self.get_mitigation_measures('SQL Injection')
                ))
            # Password field check
            if 'input type="text"' in content and 'name="password"' not in content:
                bug_report.append((
                    'Insecure Password Field', url,
                    'Use a password field (type="password") for password fields to protect user credentials.'
                ))
            # Add more static checks as needed
        except Exception as e:
            bug_report.append((
                'Website Scan Error', url, f"Could not scan website: {e}"
            ))
        return bug_report

    def scan_directory(self, directory_path):
        from functions.bug_exp import get_bug_explanation
        bug_report = []
        custom_rules = getattr(self, 'custom_rules', [])
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if file.endswith('.py'):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if 'eval(' in content:
                                bug_type = 'Eval Usage'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Avoid using eval(). Use safer alternatives.'
                                bug_report.append((bug_type, file_path, explanation))
                            if 'exec(' in content:
                                bug_type = 'Exec Usage'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Avoid using exec(). Use safer alternatives.'
                                bug_report.append((bug_type, file_path, explanation))
                            if 'pickle' in content:
                                bug_type = 'Pickle Usage'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Avoid untrusted pickle data.'
                                bug_report.append((bug_type, file_path, explanation))
                            if 'os.system' in content:
                                bug_type = 'OS Command'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Avoid os.system(). Use subprocess with shlex.quote.'
                                bug_report.append((bug_type, file_path, explanation))
                    elif file.endswith('.html') or file.endswith('.htm'):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if '<script>' in content or 'onerror=' in content:
                                bug_type = 'XSS'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Sanitize all user input and use proper escaping.'
                                bug_report.append((bug_type, file_path, explanation))
                            if 'sql' in content.lower() or 'syntax error' in content.lower():
                                bug_type = 'SQL Injection'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Use parameterized queries and ORM.'
                                bug_report.append((bug_type, file_path, explanation))
                            if 'input type="text"' in content and 'name="password"' not in content:
                                bug_type = 'Insecure Password Field'
                                explanation = get_bug_explanation(bug_type) or self.get_mitigation_measures(bug_type) or 'Use a password field (type="password") for password fields.'
                                bug_report.append((bug_type, file_path, explanation))
                except Exception as e:
                    bug_report.append(("File Read Error", file_path, f"Could not read file: {e}"))
        return bug_report

    def display_bug_report(self, bug_report):
        from functions.bug_exp import get_bug_explanation
        self.bug_list_widget.clear()
        if not bug_report:
            self.bug_list_widget.addItem("No bugs found! 😊")
        else:
            for idx, bug in enumerate(bug_report, start=1):
                if len(bug) >= 2:
                    bug_type, file_path = bug[:2]
                    explanation = bug[2] if len(bug) > 2 and bug[2] else get_bug_explanation(bug_type)
                    # Replace 'No explanation available.' with measures against the bug/vulnerability
                    if not explanation or 'No explanation available' in explanation:
                        explanation = self.get_mitigation_measures(bug_type)
                    item = QtWidgets.QListWidgetItem(f"{idx}. {bug_type}: {explanation}\nFile: {file_path}")
                    self.bug_list_widget.addItem(item)
                else:
                    self.bug_list_widget.addItem(f"Issue with bug report format: {bug}")
        self.update_dashboard()  # Always update chart after displaying bug report

    def update_dashboard(self):
        """Update the bug type distribution pie chart on the dashboard."""
        from collections import Counter
        bug_report = getattr(self, 'bug_report_data', [])
        bug_types = [b[0] for b in bug_report if len(b) > 0]
        self.dashboard_ax.clear()
        legend_html = ""
        if bug_types:
            counts = Counter(bug_types)
            labels = list(counts.keys())
            sizes = list(counts.values())
            colors = ['#00bf63', '#007bff', '#ff4d4f', '#f5f6fa', '#23272e', '#e0e0e0']
            wedges, texts, autotexts = self.dashboard_ax.pie(
                sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)],
                textprops={'color': 'white' if self.is_dark_theme else '#23272e', 'fontsize': 13}
            )
            self.dashboard_ax.set_title('Bug Type Distribution', color='#00bf63' if self.is_dark_theme else '#007bff', fontsize=16)
            # Build legend HTML
            legend_html = "<b>Legend:</b> " + " | ".join([f"<span style='color:{colors[i % len(colors)]};'>{labels[i]}</span> ({sizes[i]})" for i in range(len(labels))])
        else:
            self.dashboard_ax.text(0.5, 0.5, "No data", ha='center', va='center', fontsize=16, color='#00bf63' if self.is_dark_theme else '#007bff')
            self.dashboard_ax.set_title('Bug Type Distribution', color='#00bf63' if self.is_dark_theme else '#007bff', fontsize=16)
            legend_html = "<span style='color:#ff4d4f;'>No data to display.</span>"
        self.dashboard_canvas.draw()
        self.dashboard_legend.setText(legend_html)

    def get_mitigation_measures(self, bug_type, fallback_only=True):
        """Return recommended measures against the given bug or vulnerability type."""
        measures = {
            'Eval Usage': 'Avoid using eval(). Use safer alternatives or proper parsing.',
            'Exec Usage': 'Avoid using exec(). Use safer alternatives or proper parsing.',
            'Pickle Usage': 'Avoid untrusted pickle data. Use safer serialization like json.',
            'OS Command': 'Avoid os.system(). Use subprocess with shlex.quote and validate input.',
            'XSS': 'Sanitize all user input and use proper escaping in HTML to prevent XSS.',
            'SQL Injection': 'Use parameterized queries and ORM. Never concatenate user input in SQL. Validate and sanitize all inputs.',
            'File Read Error': 'Check file permissions and encoding. Handle exceptions gracefully.',
            'Insecure Password Field': 'Use a password field (type="password") for password fields to protect user credentials.',
            'Website Scan Error': 'The scanner was unable to scan this website. Check the URL, network connection, or if the site blocks automated requests.',
            # Add more mappings as needed
        }
        if fallback_only:
            return measures.get(bug_type, None)
        else:
            return measures.get(bug_type, 'No specific mitigation available for this issue.')

    def open_custom_rules_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Custom Scanning Rules")
        dialog.setFixedSize(500, 400)
        layout = QtWidgets.QVBoxLayout(dialog)
        rules_list = QtWidgets.QListWidget()
        for rule in self.custom_rules:
            rules_list.addItem(f"Pattern: {rule['pattern']} | Description: {rule['description']}")
        add_btn = QtWidgets.QPushButton("Add Rule")
        edit_btn = QtWidgets.QPushButton("Edit Selected")
        del_btn = QtWidgets.QPushButton("Delete Selected")
        layout.addWidget(rules_list)
        layout.addWidget(add_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
        dialog.setLayout(layout)
        def add_rule():
            pattern, ok1 = QtWidgets.QInputDialog.getText(dialog, "Add Rule", "Regex Pattern:")
            desc, ok2 = QtWidgets.QInputDialog.getText(dialog, "Add Rule", "Description:")
            if ok1 and ok2 and pattern:
                self.custom_rules.append({"pattern": pattern, "description": desc})
                rules_list.addItem(f"Pattern: {pattern} | Description: {desc}")
                if hasattr(self, 'save_custom_rules'):
                    self.save_custom_rules()
        def edit_rule():
            row = rules_list.currentRow()
            if row >= 0:
                rule = self.custom_rules[row]
                pattern, ok1 = QtWidgets.QInputDialog.getText(dialog, "Edit Rule", "Regex Pattern:", text=rule['pattern'])
                desc, ok2 = QtWidgets.QInputDialog.getText(dialog, "Edit Rule", "Description:", text=rule['description'])
                if ok1 and ok2 and pattern:
                    self.custom_rules[row] = {"pattern": pattern, "description": desc}
                    rules_list.item(row).setText(f"Pattern: {pattern} | Description: {desc}")
                    if hasattr(self, 'save_custom_rules'):
                        self.save_custom_rules()
        def del_rule():
            row = rules_list.currentRow()
            if row >= 0:
                self.custom_rules.pop(row)
                rules_list.takeItem(row)
                if hasattr(self, 'save_custom_rules'):
                    self.save_custom_rules()
        add_btn.clicked.connect(add_rule)
        edit_btn.clicked.connect(edit_rule)
        del_btn.clicked.connect(del_rule)
        dialog.exec_()

    def export_profile(self):
        from PyQt5.QtWidgets import QFileDialog
        import json
        profile = {
            'custom_rules': self.custom_rules if hasattr(self, 'custom_rules') else [],
            'theme': self.theme_preference if hasattr(self, 'theme_preference') else 'dark',
            'font': self.font_family if hasattr(self, 'font_family') else 'Segoe UI',
            'language': self.lang_combo.currentText() if hasattr(self, 'lang_combo') else 'English'
        }
        fname, _ = QFileDialog.getSaveFileName(self, "Export Profile", "profile.json", "JSON Files (*.json)")
        if fname:
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)
            QtWidgets.QMessageBox.information(self, "Export", "Profile exported successfully.")

    def import_profile(self):
        from PyQt5.QtWidgets import QFileDialog
        import json
        fname, _ = QFileDialog.getOpenFileName(self, "Import Profile", "", "JSON Files (*.json)")
        if fname:
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                self.custom_rules = profile.get('custom_rules', [])
                self.theme_preference = profile.get('theme', 'dark')
                self.font_family = profile.get('font', 'Segoe UI')
                if hasattr(self, 'lang_combo'):
                    lang = profile.get('language', 'English')
                    idx = self.lang_combo.findText(lang)
                    if idx >= 0:
                        self.lang_combo.setCurrentIndex(idx)
                QtWidgets.QMessageBox.information(self, "Import", "Profile imported successfully.")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Import Error", f"Failed to import profile: {e}")

    def save_user_info(self, name, pixmap):
        self.user_info['name'] = name
        # Avatar path already set in change_avatar
        import json
        with open('user_profile.json', 'w', encoding='utf-8') as f:
            json.dump(self.user_info, f, indent=2)
        QtWidgets.QMessageBox.information(self, "Profile", "User profile saved.")
        self.update_user_display()

    def load_user_info(self):
        import json
        if os.path.exists('user_profile.json'):
            try:
                with open('user_profile.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {'name': 'User', 'avatar': 'images/icon.png'}

    def update_user_display(self):
        # Update Home and Settings pages with user name/avatar
        if hasattr(self, 'home_user_label'):
            self.home_user_label.setText(self.user_info.get('name', 'User'))
        if hasattr(self, 'settings_user_label'):
            self.settings_user_label.setText(self.user_info.get('name', 'User'))

    def check_badges(self):
        new_badges = []
        if self.scan_count >= 1 and 'First Scan' not in self.badges:
            new_badges.append('First Scan')
        if self.scan_count >= 10 and 'Scan Master' not in self.badges:
            new_badges.append('Scan Master')
        if self.bug_count >= 1 and 'Bug Hunter' not in self.badges:
            new_badges.append('Bug Hunter')
        if self.bug_count >= 20 and 'Bug Slayer' not in self.badges:
            new_badges.append('Bug Slayer')
        for badge in new_badges:
            self.badges.append(badge)
        self.save_gamification_state()
        self.update_badge_display()

    def save_gamification_state(self):
        import json
        self.user_info['badges'] = self.badges
        self.user_info['scan_count'] = self.scan_count
        self.user_info['bug_count'] = self.bug_count
        with open('user_profile.json', 'w', encoding='utf-8') as f:
            json.dump(self.user_info, f, indent=2)

    def update_badge_display(self):
        # Optionally update a badge display widget if present
        pass

    def export_bug_report_qr(self):
        from PyQt5.QtWidgets import QFileDialog
        if not hasattr(self, 'bug_report_data') or not self.bug_report_data:
            QtWidgets.QMessageBox.warning(self, "No Data", "No bug report data to export.")
            return
        # Prepare data as a readable, formatted string
        lines = ["Bfinder Bug Report\n"]
        for idx, bug in enumerate(self.bug_report_data, start=1):
            bug_type = bug[0] if len(bug) > 0 else ''
            file_url = bug[1] if len(bug) > 1 else ''
            mitigation = bug[2] if len(bug) > 2 else ''
            lines.append(f"Bug {idx}:")
            lines.append(f"  Type: {bug_type}")
            lines.append(f"  File/URL: {file_url}")
            lines.append(f"  Mitigation: {mitigation}")
            lines.append("")  # Blank line between bugs
        data = '\n'.join(lines)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        fname, _ = QFileDialog.getSaveFileName(self, "Export QR Code", "bug_report.png", "PNG Files (*.png)")
        if fname:
            img.save(fname)
            QtWidgets.QMessageBox.information(self, "Export", "QR code exported successfully.")

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_preference = 'dark' if self.is_dark_theme else 'light'
        if self.is_dark_theme:
            self.setStyleSheet("background: #23272e; color: #f5f6fa; font-family: 'Segoe UI', 'Cantarell', 'Arial', sans-serif; font-size: 16px;")
            self.sidebar.setStyleSheet("background: #181a20; border-right: 1px solid #00bf63;")
            self.top_bar.setStyleSheet("background: #181a20; height: 60px; border-bottom: 1px solid #00bf63;")
            self.theme_switch.setText("Switch to Light Theme")
        else:
            self.setStyleSheet("background: #f5f6fa; color: #23272e; font-family: 'Segoe UI', 'Cantarell', 'Arial', sans-serif; font-size: 16px;")
            self.sidebar.setStyleSheet("background: #e0e0e0; border-right: 1px solid #00bf63;")
            self.top_bar.setStyleSheet("background: #e0e0e0; height: 60px; border-bottom: 1px solid #00bf63;")
            self.theme_switch.setText("Switch to Dark Theme")
        sidebar_color = '#181a20' if self.is_dark_theme else '#e0e0e0'
        text_color = '#f5f6fa' if self.is_dark_theme else '#23272e'
        btn_color = '#00bf63' if self.is_dark_theme else '#007bff'
        for i in range(0, self.sidebar_layout.count()):
            item = self.sidebar_layout.itemAt(i).widget()
            if isinstance(item, QtWidgets.QPushButton):
                item.setStyleSheet(f"padding: 14px; font-size: {self.font_size}px; border-radius: 10px; background: {sidebar_color}; color: {btn_color}; font-weight: 600;")
        self.top_bar.setStyleSheet(f"background: {sidebar_color}; height: 60px; border-bottom: 1px solid {btn_color};")
        self.logo.setStyleSheet("image: url(images/logo.png);")
        self.title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {btn_color}; letter-spacing: 2px;")
        self.user_label.setStyleSheet(f"font-size: 16px; color: {text_color};")
        for page in [self.page_home, self.page_bug, self.page_tips, self.page_doc, self.page_settings, self.page_analytics, self.page_dashboard]:
            page.setStyleSheet(f"background: {'#23272e' if self.is_dark_theme else '#f5f6fa'}; color: {text_color};")
        for button in [getattr(self, n, None) for n in [
            'bug_browse_btn', 'bug_scan_website_btn', 'print_report_btn', 'export_qr_btn', 'github_issue_btn', 'lint_btn'
        ] if hasattr(self, n)]:
            if button:
                button.setStyleSheet(f"padding: 10px; font-size: {self.font_size}px; border-radius: 8px; background: {btn_color}; color: white;")
        self.bug_list_widget.setStyleSheet(f"background: {'#23272e' if self.is_dark_theme else '#f5f6fa'}; border: 1px solid {btn_color}; border-radius: 8px; color: {text_color}; font-size: 14px;")
        if self.analytics_label:
            self.analytics_label.setStyleSheet(f"color: {btn_color};")
        if self.dashboard_label:
            self.dashboard_label.setStyleSheet(f"color: {btn_color};")
        if self.threat_label:
            self.threat_label.setStyleSheet(f"color: {btn_color};")
        self.lang_combo.setStyleSheet(f"font-size: 15px; background: #23272e; color: #00bf63; border-radius: 6px;")
        # Ensure font and color consistency everywhere
        self.set_fonts_and_colors()

    def set_fonts_and_colors(self):
        """Ensure consistent font and color for all widgets, including sidebar buttons, after theme/font change."""
        font = QtGui.QFont(self.font_family, self.font_size)
        self.setFont(font)
        self.set_fonts_recursive(self.centralWidget())
        # Sidebar buttons
        sidebar_color = '#181a20' if self.is_dark_theme else '#e0e0e0'
        btn_color = '#00bf63' if self.is_dark_theme else '#007bff'
        for i in range(self.sidebar_layout.count()):
            item = self.sidebar_layout.itemAt(i).widget()
            if isinstance(item, QtWidgets.QPushButton):
                item.setFont(font)
                item.setStyleSheet(f"padding: 14px; font-size: {self.font_size}px; border-radius: 10px; background: {sidebar_color}; color: {btn_color}; font-weight: 600;")
        # Top bar labels
        if hasattr(self, 'title'):
            self.title.setFont(font)
        if hasattr(self, 'user_label'):
            self.user_label.setFont(font)
        # Update bug list widget font
        if hasattr(self, 'bug_list_widget'):
            self.bug_list_widget.setFont(font)
        # Update other key widgets as needed

    # In toggle_theme, after all style changes, call set_fonts_and_colors
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_preference = 'dark' if self.is_dark_theme else 'light'
        if self.is_dark_theme:
            self.setStyleSheet("background: #23272e; color: #f5f6fa; font-family: 'Segoe UI', 'Cantarell', 'Arial', sans-serif; font-size: 16px;")
            self.sidebar.setStyleSheet("background: #181a20; border-right: 1px solid #00bf63;")
            self.top_bar.setStyleSheet("background: #181a20; height: 60px; border-bottom: 1px solid #00bf63;")
            self.theme_switch.setText("Switch to Light Theme")
        else:
            self.setStyleSheet("background: #f5f6fa; color: #23272e; font-family: 'Segoe UI', 'Cantarell', 'Arial', sans-serif; font-size: 16px;")
            self.sidebar.setStyleSheet("background: #e0e0e0; border-right: 1px solid #00bf63;")
            self.top_bar.setStyleSheet("background: #e0e0e0; height: 60px; border-bottom: 1px solid #00bf63;")
            self.theme_switch.setText("Switch to Dark Theme")
        sidebar_color = '#181a20' if self.is_dark_theme else '#e0e0e0'
        text_color = '#f5f6fa' if self.is_dark_theme else '#23272e'
        btn_color = '#00bf63' if self.is_dark_theme else '#007bff'
        for i in range(0, self.sidebar_layout.count()):
            item = self.sidebar_layout.itemAt(i).widget()
            if isinstance(item, QtWidgets.QPushButton):
                item.setStyleSheet(f"padding: 14px; font-size: {self.font_size}px; border-radius: 10px; background: {sidebar_color}; color: {btn_color}; font-weight: 600;")
        self.top_bar.setStyleSheet(f"background: {sidebar_color}; height: 60px; border-bottom: 1px solid {btn_color};")
        self.logo.setStyleSheet("image: url(images/logo.png);")
        self.title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {btn_color}; letter-spacing: 2px;")
        self.user_label.setStyleSheet(f"font-size: 16px; color: {text_color};")
        for page in [self.page_home, self.page_bug, self.page_tips, self.page_doc, self.page_settings, self.page_analytics, self.page_dashboard]:
            page.setStyleSheet(f"background: {'#23272e' if self.is_dark_theme else '#f5f6fa'}; color: {text_color};")
        for button in [getattr(self, n, None) for n in [
            'bug_browse_btn', 'bug_scan_website_btn', 'print_report_btn', 'export_qr_btn', 'github_issue_btn', 'lint_btn'
        ] if hasattr(self, n)]:
            if button:
                button.setStyleSheet(f"padding: 10px; font-size: {self.font_size}px; border-radius: 8px; background: {btn_color}; color: white;")
        self.bug_list_widget.setStyleSheet(f"background: {'#23272e' if self.is_dark_theme else '#f5f6fa'}; border: 1px solid {btn_color}; border-radius: 8px; color: {text_color}; font-size: 14px;")
        if self.analytics_label:
            self.analytics_label.setStyleSheet(f"color: {btn_color};")
        if self.dashboard_label:
            self.dashboard_label.setStyleSheet(f"color: {btn_color};")
        if self.threat_label:
            self.threat_label.setStyleSheet(f"color: {btn_color};")
        self.lang_combo.setStyleSheet(f"font-size: 15px; background: #23272e; color: #00bf63; border-radius: 6px;")
        # Ensure font and color consistency everywhere
        self.set_fonts_and_colors()

    # In change_font_family and change_font_size, call set_fonts_and_colors
    def change_font_family(self, font):
        self.font_family = font.family() if hasattr(font, 'family') else str(font)
        app = QtWidgets.QApplication.instance()
        if app:
            app.setFont(QtGui.QFont(self.font_family, self.font_size))
        self.set_fonts_and_colors()
        if hasattr(self, 'font_combo'):
            self.font_combo.setCurrentFont(QtGui.QFont(self.font_family))

    def change_font_size(self, size):
        self.font_size = size
        app = QtWidgets.QApplication.instance()
        if app:
            app.setFont(QtGui.QFont(self.font_family, self.font_size))
        self.set_fonts_and_colors()
        if hasattr(self, 'font_size_spin'):
            self.font_size_spin.setValue(self.font_size)

    def set_fonts_recursive(self, widget):
        """Recursively set font for all child widgets."""
        font = QtGui.QFont(self.font_family, self.font_size)
        widget.setFont(font)
        for child in widget.findChildren(QtWidgets.QWidget):
            child.setFont(font)

    def change_language(self, lang):
        """Change the application's language (UI text)."""
        # Example: Only updates the window title and a few labels for demo. Extend as needed.
        translations = {
            'English': {
                'window_title': 'Bfinder',
                'settings': 'Settings',
                'dashboard': 'Dashboard',
                'bug_report': 'Bug Report',
                'security_tips': 'Security Tips',
                'documentation': 'Documentation',
                'analytics': 'Analytics',
                'report_bug': 'Report a Bug',
                'home': 'Home',
            },
            'Spanish': {
                'window_title': 'Bfinder',
                'settings': 'Configuración',
                'dashboard': 'Tablero',
                'bug_report': 'Informe de errores',
                'security_tips': 'Consejos de seguridad',
                'documentation': 'Documentación',
                'analytics': 'Analítica',
                'report_bug': 'Reportar un error',
                'home': 'Inicio',
            },
            'French': {
                'window_title': 'Bfinder',
                'settings': 'Paramètres',
                'dashboard': 'Tableau de bord',
                'bug_report': 'Rapport de bogue',
                'security_tips': 'Conseils de sécurité',
                'documentation': 'Documentation',
                'analytics': 'Analytique',
                'report_bug': 'Signaler un bug',
                'home': 'Accueil',
            },
            'German': {
                'window_title': 'Bfinder',
                'settings': 'Einstellungen',
                'dashboard': 'Instrumententafel',
                'bug_report': 'Fehlerbericht',
                'security_tips': 'Sicherheitstipps',
                'documentation': 'Dokumentation',
                'analytics': 'Analytik',
                'report_bug': 'Fehler melden',
                'home': 'Startseite',
            },
        }
        t = translations.get(lang, translations['English'])
        self.setWindowTitle(t['window_title'])
        if hasattr(self, 'settings_label'):
            self.settings_label.setText(f"<h2 style='color:#00bf63;'>{t['settings']}</h2>")
        if hasattr(self, 'dashboard_label'):
            self.dashboard_label.setText(f"<h2 style='color:#00bf63;'>{t['dashboard']}</h2>")
        if hasattr(self, 'bug_list_widget'):
            self.page_bug.setWindowTitle(t['bug_report'])
        if hasattr(self, 'page_tips'):
            for i in range(self.page_tips.layout().count()):
                w = self.page_tips.layout().itemAt(i).widget()
                if isinstance(w, QtWidgets.QLabel) and 'Security Tips' in w.text():
                    w.setText(f"<h2 style='color:#00bf63;'>{t['security_tips']}</h2>")
        if hasattr(self, 'page_doc'):
            for i in range(self.page_doc.layout().count()):
                w = self.page_doc.layout().itemAt(i).widget()
                if isinstance(w, QtWidgets.QLabel) and 'Documentation' in w.text():
                    w.setText(f"<h2 style='color:#00bf63;'>{t['documentation']}</h2>")
        if hasattr(self, 'analytics_label'):
            self.analytics_label.setText(f"<h2 style='color:#00bf63;'>{t['analytics']}</h2>")
        # Sidebar buttons (update their text)
        if hasattr(self, 'btn_dashboard'):
            self.btn_dashboard.setText(t['dashboard'])
        if hasattr(self, 'btn_home'):
            self.btn_home.setText(t['home'])
        if hasattr(self, 'btn_bug'):
            self.btn_bug.setText(t['bug_report'])
        if hasattr(self, 'btn_tips'):
            self.btn_tips.setText(t['security_tips'])
        if hasattr(self, 'btn_doc'):
            self.btn_doc.setText(t['documentation'])
        if hasattr(self, 'btn_settings'):
            self.btn_settings.setText(t['settings'])
        if hasattr(self, 'btn_analytics'):
            self.btn_analytics.setText(t['analytics'])
        if hasattr(self, 'btn_report_bug'):
            self.btn_report_bug.setText(t['report_bug'])

    def change_password_dialog(self):
        """Show a premium, branded password change dialog."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Change Password")
        dialog.setFixedSize(400, 320)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23272e, stop:1 #00bf63);
                border-radius: 22px;
                border: 2px solid #00bf63;
            }
        """)
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(36)
        shadow.setColor(QtGui.QColor(0, 191, 99, 120))
        shadow.setOffset(0, 10)
        dialog.setGraphicsEffect(shadow)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)
        # Title
        title = QtWidgets.QLabel("<span style='font-size:26px; font-weight:bold; color:#00bf63;'>Change Password</span>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        # Subtitle
        subtitle = QtWidgets.QLabel("<span style='font-size:15px;color:#f5f6fa;'>Update your password for better security.</span>")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle)
        # Error/success message area
        msg_label = QtWidgets.QLabel("")
        msg_label.setAlignment(QtCore.Qt.AlignCenter)
        msg_label.setStyleSheet("font-size:15px;color:#ff4d4f;")
        layout.addWidget(msg_label)
        # Form fields
        old_pass_label = QtWidgets.QLabel("Current Password:")
        old_pass_label.setStyleSheet("color:#00bf63;font-size:15px;")
        old_pass_input = QtWidgets.QLineEdit()
        old_pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        new_pass_label = QtWidgets.QLabel("New Password:")
        new_pass_label.setStyleSheet("color:#00bf63;font-size:15px;")
        new_pass_input = QtWidgets.QLineEdit()
        new_pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        confirm_pass_label = QtWidgets.QLabel("Confirm New Password:")
        confirm_pass_label.setStyleSheet("color:#00bf63;font-size:15px;")
        confirm_pass_input = QtWidgets.QLineEdit()
        confirm_pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        submit_btn = QtWidgets.QPushButton("Change Password")
        submit_btn.setStyleSheet("padding: 12px; font-size: 16px; border-radius: 10px; background: #181a20; color: #00bf63; font-weight: bold;")
        for w in [old_pass_label, old_pass_input, new_pass_label, new_pass_input, confirm_pass_label, confirm_pass_input, submit_btn]:
            layout.addWidget(w)
        dialog.setLayout(layout)

        def get_stored_password():
            try:
                pw = keyring.get_password("system", "user")
                if pw:
                    return pw
            except Exception:
                pass
            try:
                with open("system_password.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                return "1234"  # Default fallback

        def set_stored_password(new_pw):
            try:
                keyring.set_password("system", "user", new_pw)
                return True
            except Exception:
                try:
                    with open("system_password.txt", "w", encoding="utf-8") as f:
                        f.write(new_pw)
                    return True
                except Exception:
                    return False

        def handle_submit():
            old_pw = old_pass_input.text()
            new_pw = new_pass_input.text()
            confirm_pw = confirm_pass_input.text()
            stored_pw = get_stored_password()
            if old_pw != stored_pw:
                msg_label.setText("Current password is incorrect.")
                msg_label.setStyleSheet("font-size:15px;color:#ff4d4f;")
                return
            if not new_pw or len(new_pw) < 4:
                msg_label.setText("New password must be at least 4 characters.")
                msg_label.setStyleSheet("font-size:15px;color:#ff4d4f;")
                return
            if new_pw != confirm_pw:
                msg_label.setText("New passwords do not match.")
                msg_label.setStyleSheet("font-size:15px;color:#ff4d4f;")
                return
            if set_stored_password(new_pw):
                msg_label.setText("Password changed successfully!")
                msg_label.setStyleSheet("font-size:15px;color:#00bf63;")
                QtCore.QTimer.singleShot(1200, dialog.accept)
            else:
                msg_label.setText("Failed to save new password.")
                msg_label.setStyleSheet("font-size:15px;color:#ff4d4f;")

        submit_btn.clicked.connect(handle_submit)
        old_pass_input.setFocus()
        dialog.exec_()

    def show_login_dialog(self):
        """Show a secure login dialog before the welcome popup or main window."""
        login = LoginDialog(self)
        return login.exec_() == QtWidgets.QDialog.Accepted

    def show_welcome_popup(self):
        """Show the premium WelcomePopup dialog (class-based, not inline)."""
        popup = WelcomePopup(self)
        # Removed: popup.exec_()  # Already called in WelcomePopup.__init__()

    def animate_sidebar_highlight(self, idx):
        # Switch stacked widget page based on sidebar button index
        page_widgets = [
            self.page_dashboard, self.page_home, self.page_bug, self.page_tips, self.page_doc, self.page_settings,
            self.page_analytics, None  # btn_report_bug (None)
        ]
        if 0 <= idx < len(page_widgets) and page_widgets[idx] is not None:
            self.stacked_widget.setCurrentWidget(page_widgets[idx])
        # Optionally animate the highlight bar here if desired

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ModernMainWindow()
    window.show()
    sys.exit(app.exec_())
