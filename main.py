from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget, QMainWindow, QApplication, QStyle, QMenu, QAction, QActionGroup, QDialog, qApp, QMessageBox
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, Qt, QTimer, QCoreApplication, QProcess, QSettings, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
import PyQt5
import miniaudio
import os
import re
from datetime import datetime
import sys
from rich import print
import urllib.request
import webbrowser
from functools import partial
import threading
import qdarktheme
from win10toast import ToastNotifier

'''
Development setup
first pip install virtualenv

create virtual env with:
virtualenv venv

then activate venv

then install
pip install win10toast pyqt5 miniaudio pyinstaller pyqtdarktheme

To build
pyinstaller -F --icon=icons/icon.ico --hidden-import=_cffi_backend main.py
'''

__author__ = "Jared Gross"
__copyright__ = "Copyright 2021, TheCodingJ's"
__credits__: "list[str]" = ["Jared Gross"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Jared Gross"
__email__ = "jared@pinelandfarms.ca"
__status__ = "Production"

toaster = ToastNotifier()

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn

    @pyqtSlot()
    def run(self):
        self.fn()

class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

class Button(QPushButton):
    entered = pyqtSignal()
    leaved = pyqtSignal()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.entered.emit()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.leaved.emit()

class licensewindowUI(QDialog):
    def __init__(self):
        super(licensewindowUI, self).__init__()
        uic.loadUi('license.ui', self)
        self.setWindowTitle("License")
        self.settings = QSettings("A", "B")
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
        self.icon = self.findChild(QLabel, 'lblIcon')
        self.icon.setFixedSize(128, 128)
        pixmap = QPixmap('icons/icon.png')
        myScaledPixmap = pixmap.scaled(self.icon.size(), Qt.KeepAspectRatio)
        self.icon.setPixmap(myScaledPixmap)
        self.lisenceText = self.findChild(QLabel, 'label_2')
        with open('LICENSE', 'r') as f:
            self.lisenceText.setText(f.read())
        self.btnClose = self.findChild(QPushButton, 'btnClose')
        self.btnClose.clicked.connect(self.close)
        self.setFixedSize(780, 470)
        if self.settings.contains("Dark theme") and self.settings.value("Dark theme") == 'true':
            self.toggle_darktheme()
        else:
            self.toggle_lighttheme()

    def toggle_darktheme(self):
        self.setStyleSheet(qdarktheme.load_stylesheet())

    def toggle_lighttheme(self):
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.hbni_html: str
        self.active_events: str
        self.active_listeners: str
        self.active_streams: str
        self.threadpool: QThreadPool() = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.event_stop = threading.Event()
        self.startTime: datetime.now() = datetime.now()
        self.currentTime: datetime.now() = datetime.now()
        self.settings = QSettings("A", "B")
        self.streamPlaying: bool = False
        self.streamsOnline: bool = False
        self.streamsForceStop: bool = False
        self.enabledNotifications: bool = True
        self.darkThemeEnabled: bool = False

        layout: QVBoxLayout() = QVBoxLayout()

        self.layoutStreams: QVBoxLayout() = QVBoxLayout()

        self.setWindowIcon(QIcon('icons/icon.png'))

        self.hbnilogo: QLabel() = QLabel()
        self.hbnilogo.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.hbnilogo)

        header: QLabel() = QLabel("<h1>HBNI Audio Stream Listener</h1>")
        header.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(header)

        self.lblCallBack: QLabel() = QLabel()
        self.lblCallBack.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.lblCallBack)

        self.lblActiveListeners: QLabel() = QLabel('Loading...')
        self.lblActiveListeners.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        # btnStream: QPushButton = QPushButton("RESTART")
        # btnStream.setFixedSize(200, 60)
        # btnStream.pressed.connect(restart)
        # btnStream.pressed.connect(partial(self.listen_to_stream, ''))
        # layout.addWidget(btnStream, alignment=Qt.AlignCenter)

        layout.addLayout(self.layoutStreams)

        layout.addWidget(self.lblActiveListeners)

        self.btnKillAllStreams: Button = Button(' Stop')
        self.btnKillAllStreams.clicked.connect(partial(self.kill_all_threads, True))
        self.btnKillAllStreams.setFixedSize(200, 60)
        self.btnKillAllStreams.setVisible(False)
        self.btnKillAllStreams.entered.connect(self.handle_entered)
        self.btnKillAllStreams.leaved.connect(self.handle_leaved)
        self.btnKillAllStreams.setStyleSheet('font-size: 22px')
        layout.addWidget(self.btnKillAllStreams, alignment=Qt.AlignCenter)

        w: QWidget() = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)
        self.setWindowTitle("HBNI Audio Stream Listener")

        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        settingsMenu = QMenu("Settings", self)

        checkBox = QAction('Auto start stream', self, checkable=True)
        if self.settings.contains("Auto start stream"):
            checkBox.setChecked(True if self.settings.value("Auto start stream") == 'true' else False)
        checkBox.toggled.connect(partial(self.saved_toggle_menu_settings, checkBox))
        settingsMenu.addAction(checkBox)

        checkBox = QAction('Enable notifications', self, checkable=True)
        checkBox.setChecked(True)
        checkBox.toggled.connect(partial(self.saved_toggle_menu_settings, checkBox))
        if self.settings.contains("Enable notifications"):
            checkBox.setChecked(True if self.settings.value("Enable notifications") == 'true' else False)
            self.enabledNotifications = True if self.settings.value("Enable notifications") == 'true' else False
        settingsMenu.addAction(checkBox)

        checkBox = QAction('Dark theme', self, checkable=True)
        if self.settings.contains("Dark theme"):
            checkBox.setChecked(True if self.settings.value("Dark theme") == 'true' else False)
            if checkBox.isChecked():
                self.darkThemeEnabled = True
                self.toggle_darktheme()
            elif not checkBox.isChecked():
                self.darkThemeEnabled = False
                self.toggle_lighttheme()

        checkBox.toggled.connect(partial(self.saved_toggle_menu_settings, checkBox))
        settingsMenu.addAction(checkBox)

        aboutMenu = QMenu("About", self)
        actionAbout_Qt = QAction('About Qt', self)
        actionAbout_Qt.triggered.connect(qApp.aboutQt)
        aboutMenu.addAction(actionAbout_Qt)

        actionAbout = QAction('About', self)
        actionAbout.triggered.connect(self.open_about_window)
        aboutMenu.addAction(actionAbout)

        actionLicense = QAction('License', self)
        actionLicense.triggered.connect(self.open_license_window)
        aboutMenu.addAction(actionLicense)

        self.menuBar().addMenu(settingsMenu)
        self.menuBar().addMenu(aboutMenu)
        self.resize(480, 640)

        self.timerCheckForStreams = QTimer()
        self.timerCheckForStreams.setInterval(1000)
        self.timerCheckForStreams.timeout.connect(self.check_for_website_changes)
        self.timerCheckForStreams.start()

        self.timerUpdateTimer = QTimer()
        self.timerUpdateTimer.setInterval(1000)
        self.timerUpdateTimer.timeout.connect(self.update_timer)
        self.timerUpdateTimer.start()

        self.show()

    def open_about_window(self):
        QMessageBox.information(self, f'HBNI Audio Stream Listener', f"Developed by: TheCodingJ's", QMessageBox.Ok, QMessageBox.Ok)

    def open_license_window(self):
        self.licenseUI = licensewindowUI()
        self.licenseUI.show()

    def saved_toggle_menu_settings(self, checkBox: QAction()):
        self.settings.setValue(checkBox.text(), checkBox.isChecked())
        self.btnKillAllStreams.setIcon(QIcon('icons/stop_black.png'))
        if checkBox.text() == 'Dark theme' and checkBox.isChecked():
            self.toggle_darktheme()
        elif checkBox.text() == 'Dark theme' and not checkBox.isChecked():
            self.toggle_lighttheme()

    def toggle_darktheme(self):
        self.darkThemeEnabled = True
        logo: QPixmap = QPixmap('icons/hbni_logo_dark.png')
        self.btnKillAllStreams.setIcon(QIcon('icons/stop_white.png'))
        logo = logo.scaled(200, 200, Qt.KeepAspectRatio)
        self.hbnilogo.setPixmap(logo)
        self.setStyleSheet(qdarktheme.load_stylesheet())

        # self.setPalette(DarkPalette())

    def toggle_lighttheme(self):
        self.darkThemeEnabled = False
        logo: QPixmap = QPixmap('icons/hbni_logo_light.png')
        logo = logo.scaled(200, 200, Qt.KeepAspectRatio)
        self.hbnilogo.setPixmap(logo)
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))
        # self.setPalette(QApplication.palette())

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def play_stream(self, stream_link: str):
        while not self.event_stop.is_set():
            with miniaudio.IceCastClient(stream_link) as source:
                stream = miniaudio.stream_any(source, source.audio_format)
                with miniaudio.PlaybackDevice() as self.device:
                    self.device.start(stream)
                    input()

    def listen_to_stream(self, stream_link: str) -> None:
        self.streamsForceStop = False
        self.startTime = datetime.now().replace(microsecond=0)
        self.streamPlaying = True
        self.event_stop = threading.Event()
        self.btnKillAllStreams.setVisible(True)
        self.worker = Worker(partial(self.play_stream, stream_link))
        self.threadpool.start(self.worker)

    @pyqtSlot()
    def kill_all_threads(self, pressed_by_button: bool = False):
        try:
            self.device.stop()
        except AttributeError:
            pass
        if pressed_by_button:
            self.streamsForceStop = True
        if self.streamPlaying: restart()
        self.btnKillAllStreams.setVisible(False)
        self.event_stop.set()
        self.streamPlaying = False

    def find_active_events(self, html: str) -> str:
        regex: re = r'(?=(<div class="event">))(\w|\W)*(?<=<\/div>)'
        matches = re.finditer(regex, html, re.MULTILINE)
        for match in matches:
            if 'no schedule' in match[0]:
                return ''
            return match[0]
        return ''

    def find_active_lisenters(self, html: str) -> str:
        regex: re = r'Current Number of Listeners: ([0-9]*)'
        matches = re.finditer(regex, html, re.MULTILINE)
        for match in matches:
            return match[0]
        return ''

    def find_active_streams(self, tag: str, html: str, replace_text: bool = True) -> 'list[str]':
        '''
        regex_finder finds strings after a tag using regex matching

        Args:
            tag (str): a tag in the html such as "data-mnt" or "data-streams"
            html (str): the html string to parserTest

        Returns:
            str: the string attached to the tag.
        '''
        regex = r"{}=([\"'])((?:(?=(?:\\)*)\\.|.)*?)\1".format(tag)
        matches = re.finditer(regex, html, re.MULTILINE)

        list_matches: list[str] = []

        for match in matches:
            m = match.group()
            m = m.replace(tag, '').replace('=','').replace('\'','')
            if replace_text:
                m = m.replace('/','').title()
            list_matches.append(m)
        return list_matches

    def update_timer(self):
        try:
            if self.streamPlaying:
                self.currentTime = datetime.now().replace(microsecond=0)
                timeDifference: datetime = self.currentTime - self.startTime
                self.lblActiveListeners.setText(f'{self.active_listeners}\nStreaming for:\n{timeDifference}')
            else:
                self.lblActiveListeners.setText(f'{self.active_listeners}')
        except AttributeError:
            pass

    def update_ui(self) -> None:
        QApplication.restoreOverrideCursor()
        self.clearLayout(self.layoutStreams)
        self.active_events = self.find_active_events(html=self.hbni_html)
        self.active_events = self.active_events.replace('h3', 'h1').replace('<p>', '<h2>').replace('</p>', '</h2>').replace('<p class="date">', '<h2>').replace('</div>', '</div><br>')
        if self.active_events != '' and  'No streams currently online.' in self.hbni_html:
            self.lblCallBack.setText('<h2>Upcoming Events:</h2>')
            lblEvents: ScrollLabel() = ScrollLabel()
            lblEvents.setText(self.active_events)
            self.layoutStreams.addWidget(lblEvents)
            self.lblActiveListeners.setText('')
            self.kill_all_threads()

        if 'No streams currently online.' not in self.hbni_html:
            self.clearLayout(self.layoutStreams)
            self.lblCallBack.setText('<h2>Streams currently online:</h2>')
            titles: list[str] = self.find_active_streams(tag='data-mnt', html=self.hbni_html)
            bodies: list[str] = self.find_active_streams(tag='data-stream', html=self.hbni_html)
            host_addresses: list[str] = self.find_active_streams(tag='data-mnt', html=self.hbni_html, replace_text=False)

            for title, body, host_address in zip(titles, bodies, host_addresses):
                btnStream: QPushButton = Button(f' {title} - {body}')
                btnStream.setToolTip(host_address)
                if self.darkThemeEnabled:
                    btnStream.setIcon(QIcon('icons/play_white.png'))
                else:
                    btnStream.setIcon(QIcon('icons/play_black.png'))
                # btnStream.setFixedSize(200, 60)
                btnStream.setStyleSheet('font-size: 18px')
                btnStream.setEnabled(not self.streamPlaying)
                btnStream.entered.connect(self.handle_entered)
                btnStream.leaved.connect(self.handle_leaved)
                btnStream.clicked.connect(partial(self.listen_to_stream, "http://hbniaudio.hbni.net:8000" + host_address))
                self.layoutStreams.addWidget(btnStream, alignment=Qt.AlignCenter)
                if not self.streamsOnline and self.settings.contains("Auto start stream") and self.settings.value("Auto start stream") != 'true' and self.enabledNotifications:
                    toaster.show_toast(u'HBNI Audio Stream Listener', f'{titles[0]} just started a stream.', icon_path='icon.ico', duration=3, threaded=True)
            self.streamsOnline = True

            if self.settings.contains("Auto start stream") and self.settings.value("Auto start stream") == 'true' and not self.streamPlaying and not self.streamsForceStop:
                if self.enabledNotifications:
                    toaster.show_toast(u'HBNI Audio Stream Listener', f'Autoplaying currently active stream.\n{titles[0]} - {bodies[0]}', icon_path='icon.ico', duration=3, threaded=True)
                self.listen_to_stream("http://hbniaudio.hbni.net:8000" + host_addresses[0])
        elif self.active_events == '' and 'No streams currently online.' in self.hbni_html:
            self.lblCallBack.setText('<h2>No streams currently online or events scheduled</h2>')
            self.kill_all_threads()
        if 'No streams currently online.' in self.hbni_html:
            self.streamsOnline = False
        self.active_listeners = self.find_active_lisenters(html=self.hbni_html)

    def handle_entered(self):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

    def handle_leaved(self):
        QApplication.restoreOverrideCursor()

    def open_website(self, website: str) -> None:
        webbrowser.open(website)

    def check_for_website_changes(self) -> None:
        fp = urllib.request.urlopen("http://hbniaudio.hbni.net", timeout=3)
        mybytes: str = fp.read()
        self.hbni_html = mybytes.decode("utf8")
        fp.close()
        self.update_ui()

def restart():
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)


app: QApplication([]) = QApplication([])
app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
window = MainWindow()
# app.setStyle('Fusion')
app.exec_()