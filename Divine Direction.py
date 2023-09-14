from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QCompleter, QMessageBox, QDialog, QPushButton, QLabel, QWidget, QGridLayout, QSpacerItem, QSizePolicy, QFormLayout, QFrame, QSystemTrayIcon, QMenu, QGroupBox, QCheckBox, QTimeEdit, QDateTimeEdit, QComboBox, QToolButton, QLayout, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor, QFontDatabase, QPainter, QPen, QGuiApplication, QPainterPath
from PyQt5.QtCore import center, Qt, pyqtSlot, QUrl, QTime, QCoreApplication, QTime, QTimer, QMetaObject, QObject, Qt, QByteArray, QSize, QRectF
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWebEngineWidgets import QWebEngineView
from tinydb import TinyDB, Query
from datetime import datetime, timedelta, date
from configparser import ConfigParser
from hijri_converter import convert
import os
import requests
import pandas as pd
import sys
import winreg
import jdatetime

#------------path------------
class os_dir(object):
    config = ConfigParser()
    Current_dir = os.path.dirname(os.path.abspath(__file__))
    Setting_path = os.path.join(Current_dir, 'img', 'cog.svg')
    AboutMe_path = os.path.join(Current_dir, 'img', 'info.svg')
    combobox = os.path.join(Current_dir, 'Azan')
    DataBaseOS = os.path.join(Current_dir, 'Data', 'Setting.json')
    DataBase_path = os.path.join(Current_dir, 'Data', 'Azan.json')
    data_path = os.path.join(Current_dir, 'data')
    ini = os.path.join(Current_dir, "config.ini")
    font = os.path.join(Current_dir, "font", "Font.TTF")
    font2 = os.path.join(Current_dir, "font", "Font2.TTF")
    font3 = os.path.join(Current_dir, "font", "Font3.TTF")
    config.read(ini)
    icon = config["Images"]['icon']
    Calendar_path = QByteArray.fromBase64(icon.encode('utf-8'))

#------------Variable------------
mediaPlayer = QMediaPlayer()
AzanPlayer = QMediaPlayer()
config = ConfigParser()
DataBase = TinyDB(os_dir.DataBaseOS)
stopAzanPlayer = False
SettingDialogClose = {"city": False}
Cancel_clicked_Variable = False
lineEditChanged__Variable = False

def CheckNetwork():
    url = 'https://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        a = QApplication(sys.argv)
        icon = QIcon()
        Calendar_Pixmap = QPixmap()
        Calendar_Pixmap.loadFromData(os_dir.Calendar_path)
        icon.addPixmap(Calendar_Pixmap, QIcon.Normal, QIcon.Off)
        a.setWindowIcon(icon)
        QMessageBox.critical(None, "خطا", "شما به اینترنت متصل نیستید")
        sys.exit()

if __name__ == '__main__':
    Azandb = TinyDB(os_dir.DataBase_path)
    AllAzan = Azandb.all()[0]
    if AllAzan['gregorian']['dategregorianIso'] is None or AllAzan['gregorian']['dategregorianIso'] != date.today().isoformat():
        CheckNetwork()

#------------Month Variable------------
shamsi_months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
gregorian_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
hijri_months = ["محرم", "صفر", "ربيع الأول", "ربيع الثاني", "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

#------------weekdays Variable------------
shamsi_weekdays = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
hijri_weekdays = ["السبت", "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"]
gregorian_weekdays = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

#------------API------------
class owghat_info(object):
    def __init__(self):
        super(owghat_info, self).__init__()
        self.Azandb = TinyDB(os_dir.DataBase_path)
        self.AllAzan = self.Azandb.all()[0]
        
        if self.AllAzan['gregorian']['dategregorianIso'] is None or self.AllAzan['gregorian']['dategregorianIso'] != date.today().isoformat():
            self.AzanDataBase = TinyDB(os_dir.DataBase_path)
            AllSetting = DataBase.all()[0]
            city = AllSetting['region']
            self.AllAzandb = self.AzanDataBase.all()[0]
            #apis
            owghat = requests.get(f'http://api.aladhan.com/v1/timingsByCity?city={city}&country=iran&method=7&tune=0,0,0,0,0,0,0,0,-42').json()
            self.hadis = requests.get('https://api.keybit.ir/hadis').json()
            
            today_shamsi = jdatetime.date.today()
            today_hijri = convert.Gregorian.today().to_hijri()
            today_gregorian = jdatetime.date.today().togregorian()

            # info owghat
            self.Azan_Sobh_Owghat = owghat['data']['timings']['Fajr']
            self.Azan_zohr_Owghat = owghat['data']['timings']['Dhuhr']
            self.Azan_Maghreb_Owghat = owghat['data']['timings']['Maghrib']
            self.Tolu_Aftab_Owghat = owghat['data']['timings']['Sunrise']
            self.Ghorub_Aftab_Owghat = owghat['data']['timings']['Sunset']
            self.Nimeshab_Owghat = owghat['data']['timings']['Midnight']

            self.date_weekday = today_shamsi.weekday()

            # shamsi
            self.year_shamsi = today_shamsi.year
            self.month_shamsi = today_shamsi.month
            self.day_shamsi = today_shamsi.day

            # hijri
            self.year_hijri = today_hijri.year
            self.month_hijri = today_hijri.month
            self.day_hijri = today_hijri.day

            # gregorian
            self.year_gregorian = today_gregorian.year
            self.month_gregorian = today_gregorian.month
            self.day_gregorian = today_gregorian.day

            self.gregorian_letters = f"{gregorian_weekdays[self.date_weekday]}, {self.day_gregorian} {gregorian_months[self.month_gregorian - 1]}, {self.year_gregorian}"
            self.gregorian = f"{self.year_gregorian}/{self.month_gregorian}/{self.day_gregorian}"

            self.shamsi_letters = f"{shamsi_weekdays[self.date_weekday]}, {self.day_shamsi} {shamsi_months[self.month_shamsi - 1]}, {self.year_shamsi}"
            self.shamsi = f"{self.year_shamsi}/{self.month_shamsi}/{self.day_shamsi}"

            self.hijri_letters = f"{hijri_weekdays[self.date_weekday]}, {self.day_hijri} {hijri_months[self.month_hijri - 1]}, {self.year_hijri}"
            self.hijri = f"{self.year_hijri}/{self.month_hijri}/{self.day_hijri}"

            self.hadis_text_Owghat = self.hadis['result']['text']
            self.hadis_person_Owghat = self.hadis['result']['person']
            self.hadis_source_Owghat = self.hadis['result']['source']

            WeekdaySTR = f"image{self.date_weekday + 1}"

            self.info = self.AzanDataBase.update({
                'weekday': self.date_weekday,
                "shamsi":{'dateshamsi': self.shamsi, "year_shamsi":self.year_shamsi, "month_shamsi":self.month_shamsi, "day_shamsi":self.day_shamsi, "letters": self.shamsi_letters},
                "hijri":{'datehijri': self.hijri, "year_hijri":self.year_hijri, "month_hijri":self.month_hijri, "day_hijri":self.day_hijri, "letters": self.hijri_letters},
                "gregorian":{'dategregorianIso': date.today().isoformat(), 'dategregorian': self.gregorian, "year_gregorian":self.year_gregorian, "month_gregorian":self.month_gregorian, "day_gregorian":self.day_gregorian, "letters": self.gregorian_letters},
                'Hadis': {'Hadis_Text': self.hadis_text_Owghat, 'Hadis_Person': self.hadis_person_Owghat, "Hadis_Source": self.hadis_source_Owghat},
                'iniNumber': WeekdaySTR,
                'AzanSobh': self.Azan_Sobh_Owghat,
                'Azanzohr': self.Azan_zohr_Owghat,
                'AzanMaghreb': self.Azan_Maghreb_Owghat,
                'ToluAftab': self.Tolu_Aftab_Owghat,
                'GhorubAftab': self.Ghorub_Aftab_Owghat,
                'Nimeshab': self.Nimeshab_Owghat
            }, doc_ids=[1])

            self.Azan_Sobh = self.AllAzandb['AzanSobh']
            self.Azan_zohr = self.AllAzandb['Azanzohr']
            self.Azan_Maghreb = self.AllAzandb['AzanMaghreb']
            self.Tolu_Aftab = self.AllAzandb['ToluAftab']
            self.Ghorub_Aftab = self.AllAzandb['GhorubAftab']
            self.Nimeshab = self.AllAzandb['Nimeshab']
            self.date_shamsi = self.AllAzandb['shamsi']['dateshamsi']
            self.shamsi_letters = self.AllAzandb['shamsi']['letters']
            self.date_ghamari = self.AllAzandb['hijri']['datehijri']
            self.ghamari_letters = self.AllAzandb['hijri']['letters']
            self.date_miladi = self.AllAzandb['gregorian']['dategregorian']
            self.miladi_letters = self.AllAzandb['gregorian']['letters']
            self.hadis_text = self.AllAzandb['Hadis']['Hadis_Text']
            self.hadis_person = self.AllAzandb['Hadis']['Hadis_Person']
            self.hadis_source = self.AllAzandb['Hadis']['Hadis_Source']
            self.iniNumber = self.AllAzandb['iniNumber']

        else:
            self.AzanDataBase = TinyDB(os_dir.DataBase_path)
            self.AllAzandb = self.AzanDataBase.all()[0]
            self.Azan_Sobh = self.AllAzandb['AzanSobh']
            self.Azan_zohr = self.AllAzandb['Azanzohr']
            self.Azan_Maghreb = self.AllAzandb['AzanMaghreb']
            self.Tolu_Aftab = self.AllAzandb['ToluAftab']
            self.Ghorub_Aftab = self.AllAzandb['GhorubAftab']
            self.Nimeshab = self.AllAzandb['Nimeshab']
            self.date_shamsi = self.AllAzandb['shamsi']['dateshamsi']
            self.shamsi_letters = self.AllAzandb['shamsi']['letters']
            self.date_ghamari = self.AllAzandb['hijri']['datehijri']
            self.ghamari_letters = self.AllAzandb['hijri']['letters']
            self.date_miladi = self.AllAzandb['gregorian']['dategregorian']
            self.miladi_letters = self.AllAzandb['gregorian']['letters']
            self.hadis_text = self.AllAzandb['Hadis']['Hadis_Text']
            self.hadis_person = self.AllAzandb['Hadis']['Hadis_Person']
            self.hadis_source = self.AllAzandb['Hadis']['Hadis_Source']
            self.iniNumber = self.AllAzandb['iniNumber']
    
if __name__ == '__main__':
    owghat_info()

from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt

class RectangleWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        rect = self.rect()
        rect.adjust(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 8, 8)

#------------UI------------
#main
class Ui_Owghat(object):
    def setupUi(self, Owghat):
        path = os_dir()
        Owghat.setObjectName("Owghat")
        Owghat.resize(530, 600)
        Owghat.setMinimumSize(530, 560)
        Owghat.setMaximumSize(600, 690)
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        Owghat.move(qr.topLeft())
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Owghat.sizePolicy().hasHeightForWidth())
        Owghat.setSizePolicy(sizePolicy)
        icon = QIcon()
        Calendar_Pixmap = QPixmap()
        Calendar_Pixmap.loadFromData(path.Calendar_path)
        icon.addPixmap(Calendar_Pixmap, QIcon.Normal, QIcon.Off)
        Owghat.setWindowIcon(icon)
        self.centralwidget = QWidget(Owghat)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(3, -1, 0, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout_3.setContentsMargins(10, 2, 5, 2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.GhamariInfo = QLabel(self.centralwidget)
        self.GhamariInfo.setObjectName("GhamariInfo")
        self.gridLayout_3.addWidget(self.GhamariInfo, 2, 0, 1, 2)
        self.ShamsiLetters = QLabel(self.centralwidget)
        self.ShamsiLetters.setObjectName("ShamsiLetters")
        self.gridLayout_3.addWidget(self.ShamsiLetters, 1, 2, 1, 1)
        self.MiladiInfo = QLabel(self.centralwidget)
        self.MiladiInfo.setObjectName("MiladiInfo")
        self.gridLayout_3.addWidget(self.MiladiInfo, 4, 0, 1, 2)
        self.Shamsi = QLabel(self.centralwidget)
        self.Shamsi.setObjectName("Shamsi")
        self.gridLayout_3.addWidget(self.Shamsi, 0, 2, 1, 1)
        self.ShamsiLettersInfo = QLabel(self.centralwidget)
        self.ShamsiLettersInfo.setObjectName("ShamsiLettersInfo")
        self.gridLayout_3.addWidget(self.ShamsiLettersInfo, 1, 0, 1, 2)
        self.Miladi = QLabel(self.centralwidget)
        self.Miladi.setObjectName("Miladi")
        self.gridLayout_3.addWidget(self.Miladi, 4, 2, 1, 1)
        self.MiladiLetters = QLabel(self.centralwidget)
        self.MiladiLetters.setObjectName("MiladiLetters")
        self.gridLayout_3.addWidget(self.MiladiLetters, 5, 2, 1, 1)
        self.Ghamari = QLabel(self.centralwidget)
        self.Ghamari.setObjectName("Ghamari")
        self.gridLayout_3.addWidget(self.Ghamari, 2, 2, 1, 1)
        self.MiladiLettersInfo = QLabel(self.centralwidget)
        self.MiladiLettersInfo.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.MiladiLettersInfo.setObjectName("MiladiLettersInfo")
        self.gridLayout_3.addWidget(self.MiladiLettersInfo, 5, 0, 1, 2)
        self.GhamariLettersInfo = QLabel(self.centralwidget)
        self.GhamariLettersInfo.setObjectName("GhamariLettersInfo")
        self.gridLayout_3.addWidget(self.GhamariLettersInfo, 3, 0, 1, 2)
        self.GhamariLetters = QLabel(self.centralwidget)
        self.GhamariLetters.setObjectName("GhamariLetters")
        self.gridLayout_3.addWidget(self.GhamariLetters, 3, 2, 1, 1)
        self.ShamsiInfo = QLabel(self.centralwidget)
        self.ShamsiInfo.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.ShamsiInfo.setObjectName("ShamsiInfo")
        self.gridLayout_3.addWidget(self.ShamsiInfo, 0, 0, 1, 2)
        config.read(os_dir.ini)
        owghatInfo = owghat_info()
        AzanDataBase = TinyDB(os_dir.DataBase_path)
        self.AllSettingAzan = AzanDataBase.all()[0]
        self.iniNumber = self.AllSettingAzan['iniNumber']
        self.weekday = config["Images"][self.iniNumber]
        self.gridLayout.addLayout(self.gridLayout_3, 0, 2, 1, 1)
        self.Zekr = QLabel(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Zekr.sizePolicy().hasHeightForWidth())
        self.Zekr.setSizePolicy(sizePolicy)
        self.Zekr.setText("")
        Zekr_pixmap = QByteArray.fromBase64(self.weekday.encode('utf-8'))
        pixmap = QPixmap()
        pixmap.loadFromData(Zekr_pixmap)
        self.Zekr.setPixmap(pixmap)
        self.Zekr.setScaledContents(False)
        self.Zekr.setObjectName("Zekr")
        self.gridLayout.addWidget(self.Zekr, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 3)
        self.cityLayout = QGridLayout()
        self.cityLayout.setContentsMargins(3, 10, 10, 10)
        self.cityLayout.setObjectName("cityLayout")
        self.setting = QPushButton(self.centralwidget)
        self.setting.setCursor(QCursor(Qt.PointingHandCursor))
        self.setting.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(path.Setting_path), QIcon.Normal, QIcon.Off)
        self.setting.setIcon(icon1)
        self.setting.setObjectName("setting")
        self.cityLayout.addWidget(self.setting, 0, 0, 1, 1)
        self.AboutMe = QPushButton(self.centralwidget)
        self.AboutMe.setCursor(QCursor(Qt.PointingHandCursor))
        self.AboutMe.setText("")
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(path.AboutMe_path), QIcon.Normal, QIcon.Off)
        self.AboutMe.setIcon(icon2)
        self.AboutMe.setObjectName("AboutMe")
        self.cityLayout.addWidget(self.AboutMe, 0, 1, 1, 1)
        self.city = QLabel(self.centralwidget)
        self.city.setObjectName("city")
        self.cityLayout.addWidget(self.city, 0, 3, 1, 1)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.cityLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.cityLayout, 8, 0, 1, 3)
        self.HorizontalLine3 = QFrame(self.centralwidget)
        self.HorizontalLine3.setFrameShadow(QFrame.Sunken)
        self.HorizontalLine3.setLineWidth(1)
        self.HorizontalLine3.setFrameShape(QFrame.HLine)
        self.HorizontalLine3.setObjectName("HorizontalLine3")
        self.gridLayout_2.addWidget(self.HorizontalLine3, 6, 0, 1, 3)
        self.hadisLayout = QGridLayout()
        self.hadisLayout.setContentsMargins(10, 5, 10, 5)
        self.hadisLayout.setVerticalSpacing(10)
        self.hadisLayout.setObjectName("hadisLayout")
        self.sourceLabel = QLabel(self.centralwidget)
        self.sourceLabel.setObjectName("sourceLabel")
        self.hadisLayout.addWidget(self.sourceLabel, 1, 0, 1, 1)
        self.HadisLabel = QLabel(self.centralwidget)
        self.HadisLabel.setObjectName("HadisLabel")
        self.hadisLayout.addWidget(self.HadisLabel, 0, 0, 1, 2)
        self.personLabel = QLabel(self.centralwidget)
        self.personLabel.setObjectName("personLabel")
        self.hadisLayout.addWidget(self.personLabel, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.hadisLayout, 5, 0, 1, 3)
        self.HorizontalLine = QFrame(self.centralwidget)
        self.HorizontalLine.setFrameShape(QFrame.HLine)
        self.HorizontalLine.setFrameShadow(QFrame.Sunken)
        self.HorizontalLine.setObjectName("HorizontalLine")
        self.gridLayout_2.addWidget(self.HorizontalLine, 2, 0, 1, 3)
        self.RoozLayout = QFormLayout()
        self.RoozLayout.setContentsMargins(40, 10, 10, 10)
        self.RoozLayout.setObjectName("RoozLayout")
        self.ToluInfo = QLabel(self.centralwidget)
        self.ToluInfo.setObjectName("ToluInfo")
        self.RoozLayout.setWidget(0, QFormLayout.LabelRole, self.ToluInfo)
        self.Tolu = QLabel(self.centralwidget)
        self.Tolu.setObjectName("Tolu")
        self.RoozLayout.setWidget(0, QFormLayout.FieldRole, self.Tolu)
        self.GhorubInfo = QLabel(self.centralwidget)
        self.GhorubInfo.setObjectName("GhorubInfo")
        self.RoozLayout.setWidget(2, QFormLayout.LabelRole, self.GhorubInfo)
        self.Ghorub = QLabel(self.centralwidget)
        self.Ghorub.setObjectName("Ghorub")
        self.RoozLayout.setWidget(2, QFormLayout.FieldRole, self.Ghorub)
        self.NimeShabInfo = QLabel(self.centralwidget)
        self.NimeShabInfo.setObjectName("NimeShabInfo")
        self.RoozLayout.setWidget(4, QFormLayout.LabelRole, self.NimeShabInfo)
        self.NimeShab = QLabel(self.centralwidget)
        self.NimeShab.setObjectName("NimeShab")
        self.RoozLayout.setWidget(4, QFormLayout.FieldRole, self.NimeShab)
        spacerItem1 = QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.RoozLayout.setItem(3, QFormLayout.SpanningRole, spacerItem1)
        spacerItem2 = QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.RoozLayout.setItem(1, QFormLayout.SpanningRole, spacerItem2)
        self.gridLayout_2.addLayout(self.RoozLayout, 0, 0, 1, 1)
        self.AzanLayout = QFormLayout()
        self.AzanLayout.setContentsMargins(40, 10, 10, 10)
        self.AzanLayout.setObjectName("AzanLayout")
        self.AzanSobhInfo = QLabel(self.centralwidget)
        self.AzanSobhInfo.setObjectName("AzanSobhInfo")
        self.AzanLayout.setWidget(0, QFormLayout.LabelRole, self.AzanSobhInfo)
        self.AzanSobh = QLabel(self.centralwidget)
        self.AzanSobh.setObjectName("AzanSobh")
        self.AzanLayout.setWidget(0, QFormLayout.FieldRole, self.AzanSobh)
        self.AzanZohrInfo = QLabel(self.centralwidget)
        self.AzanZohrInfo.setObjectName("AzanZohrInfo")
        self.AzanLayout.setWidget(2, QFormLayout.LabelRole, self.AzanZohrInfo)
        self.AzanZohr = QLabel(self.centralwidget)
        self.AzanZohr.setObjectName("AzanZohr")
        self.AzanLayout.setWidget(2, QFormLayout.FieldRole, self.AzanZohr)
        self.AzanMaghrebInfo = QLabel(self.centralwidget)
        self.AzanMaghrebInfo.setObjectName("AzanMaghrebInfo")
        self.AzanLayout.setWidget(4, QFormLayout.LabelRole, self.AzanMaghrebInfo)
        self.AzanMaghreb = QLabel(self.centralwidget)
        self.AzanMaghreb.setObjectName("AzanMaghreb")
        self.AzanLayout.setWidget(4, QFormLayout.FieldRole, self.AzanMaghreb)
        spacerItem3 = QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.AzanLayout.setItem(3, QFormLayout.SpanningRole, spacerItem3)
        spacerItem4 = QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.AzanLayout.setItem(1, QFormLayout.SpanningRole, spacerItem4)
        self.gridLayout_2.addLayout(self.AzanLayout, 0, 2, 1, 1)
        self.HorizontalLine2 = QFrame(self.centralwidget)
        self.HorizontalLine2.setFrameShadow(QFrame.Sunken)
        self.HorizontalLine2.setLineWidth(1)
        self.HorizontalLine2.setFrameShape(QFrame.HLine)
        self.HorizontalLine2.setObjectName("HorizontalLine2")
        self.gridLayout_2.addWidget(self.HorizontalLine2, 4, 0, 1, 3)
        self.VerticalLine = QFrame(self.centralwidget)
        self.VerticalLine.setFrameShape(QFrame.VLine)
        self.VerticalLine.setFrameShadow(QFrame.Sunken)
        self.VerticalLine.setObjectName("VerticalLine")
        self.gridLayout_2.addWidget(self.VerticalLine, 0, 1, 1, 1)
        spacerItem5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem5, 7, 0, 1, 3)
        self.RemainingTime = QLabel(self.centralwidget)
        self.RemainingTime.setObjectName("RemainingTime")
        self.RemainingTime.setContentsMargins(10, 10, 10, 10)
        self.gridLayout_2.addWidget(self.RemainingTime, 1, 0, 1, 3)
        self.rectangle_widget = RectangleWidget()
        self.gridLayout_2.addWidget(self.rectangle_widget, 1, 0, 1, 3)
        self.gridLayout_2.setColumnStretch(1, 10)
        Owghat.setCentralWidget(self.centralwidget)

        self.retranslateUi(Owghat)
        QMetaObject.connectSlotsByName(Owghat)

    def retranslateUi(self, Owghat):
        _translate = QCoreApplication.translate
        Owghat.setWindowTitle(_translate("Owghat", "Divine Direction"))
        Owghat.setWhatsThis(_translate("Owghat", "<html><head/><body><p>این یک برنامه ی نشان دادن اوقات شرعی است <br/>سازنده : Erfan Times</p></body></html>"))
        self.GhamariInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:9pt; font-weight:600;\">000/00/00</span></p></body></html>"))
        self.ShamsiLetters.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">:به حروف</span></p></body></html>"))
        self.MiladiInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:9pt; font-weight:600;\">000/00/00</span></p></body></html>"))
        self.Shamsi.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">:تقویم شمسی</span></p></body></html>"))
        self.ShamsiLettersInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">1402 شهریور 1, چهارشنبه</span></p></body></html>"))
        self.Miladi.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">:تقویم میلادی</span></p></body></html>"))
        self.MiladiLetters.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">:به حروف</span></p></body></html>"))
        self.Ghamari.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">:تقویم قمری</span></p></body></html>"))
        self.MiladiLettersInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">1402 شهریور 1, چهارشنبه</span></p></body></html>"))
        self.GhamariLettersInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">1402 شهریور 1, چهارشنبه</span></p></body></html>"))
        self.GhamariLetters.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">:به حروف</span></p></body></html>"))
        self.ShamsiInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:9pt; font-weight:600;\">000/00/00</span></p></body></html>"))
        self.Zekr.setToolTip(_translate("Owghat", "<html><head/><body><p>ذکر ایام هفته</p></body></html>"))
        self.setting.setToolTip(_translate("Owghat", "<html><head/><body><p>تنظیمات</p></body></html>"))
        self.AboutMe.setToolTip(_translate("Owghat", "<html><head/><body><p>درباره ی ما</p></body></html>"))
        self.city.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:16pt; font-weight:600;\">تهران</span></p></body></html>"))
        self.sourceLabel.setText(_translate("Owghat", "<html><head/><body><p><span style=\" font-size:11pt;\">منبع</span></p></body></html>"))
        self.HadisLabel.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">حدیث حدیث حدیث حدیث حدیث </span></p></body></html>"))
        self.personLabel.setText(_translate("Owghat", "<html><head/><body><p><span style=\" font-size:11pt;\">گوینده</span></p></body></html>"))
        self.ToluInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">00:00</span></p></body></html>"))
        self.Tolu.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">طلوع</span></p></body></html>"))
        self.GhorubInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">00:00</span></p></body></html>"))
        self.Ghorub.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">غروب</span></p></body></html>"))
        self.NimeShabInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">00:00</span></p></body></html>"))
        self.NimeShab.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">نیمه شب</span></p></body></html>"))
        self.AzanSobhInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">00:00</span></p></body></html>"))
        self.AzanSobh.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">اذان صبح </span></p></body></html>"))
        self.AzanZohrInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">00:00</span></p></body></html>"))
        self.AzanZohr.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">اذان ظهر </span></p></body></html>"))
        self.AzanMaghrebInfo.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">00:00</span></p></body></html>"))
        self.AzanMaghreb.setText(_translate("Owghat", "<html><head/><body><p align=\"right\"><span style=\" font-size:11pt; font-weight:600;\">اذان مغرب </span></p></body></html>"))
        self.RemainingTime.setText(_translate("Owghat", "<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:600;\">در حال محاسبه</span></p></body></html>"))

#setting
class Ui_Setting(object):
    def setupUi(self, Form):
        self.path = os_dir()
        Form.setObjectName("Form")
        Form.setFixedSize(492, 368)
        icon = QIcon()
        icon.addPixmap(QPixmap(self.path.Setting_path), QIcon.Normal, QIcon.Off)
        Form.setWindowIcon(icon)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.Save = QPushButton(Form)
        self.Save.setCursor(QCursor(Qt.PointingHandCursor))
        self.Save.setObjectName("Save")
        self.gridLayout.addWidget(self.Save, 6, 2, 1, 1)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 1)
        self.all = QGridLayout()
        self.all.setObjectName("all")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 0, 1, 1, 4)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QLineEdit(self.groupBox)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.gridLayout_4.addLayout(self.horizontalLayout, 1, 1, 1, 4)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 0, 2, 1)
        self.all.addWidget(self.groupBox, 2, 0, 1, 3)
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.all.addItem(spacerItem2, 6, 0, 1, 1)
        self.StartOnWindowsBTN = QCheckBox(Form)
        self.StartOnWindowsBTN.setCursor(QCursor(Qt.PointingHandCursor))
        self.StartOnWindowsBTN.setObjectName("StartOnWindowsBTN")
        self.all.addWidget(self.StartOnWindowsBTN, 6, 2, 1, 1)
        self.offlineMode = QCheckBox(Form)
        self.offlineMode.setCursor(QCursor(Qt.PointingHandCursor))
        self.offlineMode.setObjectName("offlineMode")
        self.all.addWidget(self.offlineMode, 6, 1, 1, 1)
        self.Azan = QGroupBox(Form)
        self.Azan.setObjectName("Azan")
        self.gridLayout_3 = QGridLayout(self.Azan)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.OpnFolder = QToolButton(self.Azan)
        self.OpnFolder.setCursor(QCursor(Qt.PointingHandCursor))
        self.OpnFolder.setObjectName("OpnFolder")
        self.horizontalLayout_3.addWidget(self.OpnFolder)
        self.Description = QLabel(self.Azan)
        self.Description.setObjectName("Description")
        self.horizontalLayout_3.addWidget(self.Description)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 2, 0, 1, 4)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.AzanMaghreb = QCheckBox(self.Azan)
        self.AzanMaghreb.setCursor(QCursor(Qt.PointingHandCursor))
        self.AzanMaghreb.setObjectName("AzanMaghreb")
        self.horizontalLayout_5.addWidget(self.AzanMaghreb)
        self.AzanZohr = QCheckBox(self.Azan)
        self.AzanZohr.setCursor(QCursor(Qt.PointingHandCursor))
        self.AzanZohr.setObjectName("AzanZohr")
        self.horizontalLayout_5.addWidget(self.AzanZohr)
        self.AzanSobh = QCheckBox(self.Azan)
        self.AzanSobh.setCursor(QCursor(Qt.PointingHandCursor))
        self.AzanSobh.setObjectName("AzanSobh")
        self.horizontalLayout_5.addWidget(self.AzanSobh)
        self.AzanLabel = QLabel(self.Azan)
        self.AzanLabel.setObjectName("AzanLabel")
        self.horizontalLayout_5.addWidget(self.AzanLabel)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 0, 0, 1, 4)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.PlayAzan = QPushButton(self.Azan)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PlayAzan.sizePolicy().hasHeightForWidth())
        self.PlayAzan.setSizePolicy(sizePolicy)
        self.PlayAzan.setMaximumSize(QSize(90, 16777215))
        self.PlayAzan.setCursor(QCursor(Qt.PointingHandCursor))
        self.PlayAzan.setObjectName("PlayAzan")
        self.horizontalLayout_4.addWidget(self.PlayAzan)
        self.Moazen = QComboBox(self.Azan)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Moazen.sizePolicy().hasHeightForWidth())
        self.Moazen.setSizePolicy(sizePolicy)
        self.Moazen.setMinimumSize(QSize(200, 0))
        self.Moazen.setCursor(QCursor(Qt.PointingHandCursor))
        self.Moazen.setObjectName("Moazen")
        self.horizontalLayout_4.addWidget(self.Moazen)
        self.MoazenLabel = QLabel(self.Azan)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MoazenLabel.sizePolicy().hasHeightForWidth())
        self.MoazenLabel.setSizePolicy(sizePolicy)
        self.MoazenLabel.setObjectName("MoazenLabel")
        self.horizontalLayout_4.addWidget(self.MoazenLabel)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 1, 0, 1, 4)
        self.all.addWidget(self.Azan, 0, 0, 1, 3)
        self.Reminder = QGroupBox(Form)
        self.Reminder.setObjectName("Reminder")
        self.gridLayout_2 = QGridLayout(self.Reminder)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.PlayReminderAzan = QCheckBox(self.Reminder)
        self.PlayReminderAzan.setCursor(QCursor(Qt.PointingHandCursor))
        self.PlayReminderAzan.setObjectName("PlayReminderAzan")
        self.gridLayout_2.addWidget(self.PlayReminderAzan, 1, 3, 1, 1, Qt.AlignRight)
        self.ReminderLabel = QLabel(self.Reminder)
        self.ReminderLabel.setObjectName("ReminderLabel")
        self.gridLayout_2.addWidget(self.ReminderLabel, 2, 3, 1, 1)
        self.TimeEdit = QTimeEdit(self.Reminder)
        self.TimeEdit.setCursor(QCursor(Qt.IBeamCursor))
        self.TimeEdit.setMaximumTime(QTime(12, 0, 0))
        self.TimeEdit.setCurrentSection(QDateTimeEdit.MinuteSection)
        self.TimeEdit.setTimeSpec(Qt.LocalTime)
        self.TimeEdit.setObjectName("TimeEdit")
        self.gridLayout_2.addWidget(self.TimeEdit, 2, 2, 1, 1)
        self.ReminderLabel2 = QLabel(self.Reminder)
        self.ReminderLabel2.setObjectName("ReminderLabel2")
        self.gridLayout_2.addWidget(self.ReminderLabel2, 2, 0, 1, 2)
        self.all.addWidget(self.Reminder, 1, 0, 1, 3)
        self.gridLayout.addLayout(self.all, 2, 0, 1, 5)
        spacerItem5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem5, 4, 0, 1, 5)
        self.Cancel = QPushButton(Form)
        self.Cancel.setCursor(QCursor(Qt.PointingHandCursor))
        self.Cancel.setObjectName("Cancel")
        self.gridLayout.addWidget(self.Cancel, 6, 1, 1, 1)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.Save, self.Cancel)
        Form.setTabOrder(self.Cancel, self.PlayReminderAzan)
        Form.setTabOrder(self.PlayReminderAzan, self.StartOnWindowsBTN)

        font = QFont('MS Shell Dlg 2', 9)
        font.setBold(False)
        self.setFont(font)

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "تنظیمات"))
        self.Save.setToolTip(_translate("Form", "<html><head/><body><p>ذخیره کردن تنظیمات</p></body></html>"))
        self.Save.setText(_translate("Form", "ذخیره"))
        self.groupBox.setTitle(_translate("Form", "انتخاب منطقه"))
        self.label.setText(_translate("Form", "<html><head/><body><p align=\"right\"><span style=\" font-size:9pt; font-weight:600;\">لطفا شهری که در ان زندگی می کنید را وارد کنید</span></p></body></html>"))
        self.lineEdit.setToolTip(_translate("Form", "انتخاب شهر یا روستا"))
        self.StartOnWindowsBTN.setToolTip(_translate("Form", "<html><head/><body><p>اجرا شدن در هنگام بالا امدن ویندوز</p></body></html>"))
        self.StartOnWindowsBTN.setText(_translate("Form", "اجرا شدن در هنگام بالا امدن ویندوز"))
        self.offlineMode.setToolTip(_translate("Form", "<html><head/><body><p>توجه بعضی قابلیت ها محدود می&zwnj;شود</p></body></html>"))
        self.offlineMode.setText(_translate("Form", "رفتن به حالت افلاین"))
        self.Azan.setTitle(_translate("Form", "اذان گو"))
        self.OpnFolder.setToolTip(_translate("Form", "<html><head/><body><p>باز کردن پوشه&zwnj;ی اذان</p></body></html>"))
        self.OpnFolder.setText(_translate("Form", "..."))
        self.Description.setText(_translate("Form", "<html><head/><body><p align=\"right\"><span style=\" font-weight:600;\">برای پخش اذان دلخواه، فایل صوتی اذان را در درون پوشه&zwnj;ی اذان بریزید</span></p></body></html>"))
        self.AzanMaghreb.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt;\">اذان مغرب</span></p></body></html>"))
        self.AzanMaghreb.setText(_translate("Form", "اذان مغرب"))
        self.AzanZohr.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt;\">اذان ظهر</span></p></body></html>"))
        self.AzanZohr.setText(_translate("Form", "اذان ظهر"))
        self.AzanSobh.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt;\">اذان صبح</span></p></body></html>"))
        self.AzanSobh.setText(_translate("Form", "اذان صبح"))
        self.AzanLabel.setText(_translate("Form", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">گفتن اذان</span></p></body></html>"))
        self.PlayAzan.setToolTip(_translate("Form", "<html><head/><body><p>پخش کردن اذان انتخاب شده</p></body></html>"))
        self.PlayAzan.setText(_translate("Form", "پخش اذان"))
        self.Moazen.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt;\">انتخاب کردن موذن</span></p></body></html>"))
        self.MoazenLabel.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">موذن</span></p></body></html>"))
        self.Reminder.setTitle(_translate("Form", "یاداوری"))
        self.PlayReminderAzan.setToolTip(_translate("Form", "<html><head/><body><p>برای یاداوری کردن شما </p></body></html>"))
        self.PlayReminderAzan.setText(_translate("Form", "پخش اذان یاداوری"))
        self.ReminderLabel.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">پخش اذان یاداوری در</span></p></body></html>"))
        self.TimeEdit.setToolTip(_translate("Form", "<html><head/><body><p>چند دقیقه/ساعت قبل از اذان یاداوری شود</p></body></html>"))
        self.ReminderLabel2.setText(_translate("Form", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">دقیقه/ساعت قبل از اذان اصلی</span></p></body></html>"))
        self.Cancel.setToolTip(_translate("Form", "<html><head/><body><p>صرف نظر کردن از ذخیره&zwnj;ی تنظیمات</p></body></html>"))
        self.Cancel.setText(_translate("Form", "صرف نظر"))

#------------Azan Goo------------
class AzanGoo(QObject):
    def __init__(self, parent=None):
        super(AzanGoo, self).__init__(parent)
        self.Time_format = "%H:%M"
        self.date = "2023-08-14 "
        self.sec = ":00"
        self.myTimer = QTimer()
        self.myTimer.timeout.connect(self.check_owghat)
        self.myTimer.start(30000) #30000

    def convert_fa_to_en_number(self, before):
        mapping = {
            '۰': '0',
            '۱': '1',
            '۲': '2',
            '۳': '3',
            '۴': '4',
            '۵': '5',
            '۶': '6',
            '۷': '7',
            '۸': '8',
            '۹': '9'
        }
        en_number = before
        for fa, en in mapping.items():
            en_number = en_number.replace(fa, en)
        return en_number

    @pyqtSlot()
    def check_owghat(self):
        TimeSetting = DataBase.all()[0]
        azan_settings = DataBase.all()[0]['Azan']
        owghat = owghat_info()
        Window = myWindow()
        current_time = datetime.now().strftime('%H:%M')
        Before = TimeSetting['reminder']['Before']

        if TimeSetting['reminder']['remindercheckBox']:
            en_number = self.convert_fa_to_en_number(Before)
            beforeFormated = timedelta(hours=int(en_number.split(':')[0]), minutes=int(en_number.split(':')[1]))
            new_AzanSobh = (datetime.strptime(owghat.Azan_Sobh, self.Time_format) - beforeFormated).strftime(self.Time_format)
            new_AzanZohr = (datetime.strptime(owghat.Azan_zohr, self.Time_format) - beforeFormated).strftime(self.Time_format)
            new_AzanMaghreb = (datetime.strptime(owghat.Azan_Maghreb, self.Time_format) - beforeFormated).strftime(self.Time_format)
            if new_AzanSobh == current_time and AzanPlayer.state() == QMediaPlayer.State.StoppedState and stopAzanPlayer == False:
                Window.PLayAzan()
                Window.new_Sobh_msg()
            if new_AzanZohr == current_time and AzanPlayer.state() == QMediaPlayer.State.StoppedState and stopAzanPlayer == False:
                Window.PLayAzan()
                Window.new_zohr_msg()
            if new_AzanMaghreb == current_time and AzanPlayer.state() == QMediaPlayer.State.StoppedState and stopAzanPlayer == False:
                Window.PLayAzan()
                Window.new_Maghreb_msg()
        if azan_settings['AzanSobh'] or azan_settings['AzanZohr'] or azan_settings['AzanMaghreb'] == True:
            if azan_settings['AzanSobh'] and AzanPlayer.state() == QMediaPlayer.State.StoppedState and stopAzanPlayer == False:
                if owghat.Azan_Sobh == current_time:
                    Window.PLayAzan()
                    Window.Sobh_MSG()
            if azan_settings['AzanZohr'] and AzanPlayer.state() == QMediaPlayer.State.StoppedState and stopAzanPlayer == False:
                if owghat.Azan_zohr == current_time:
                    Window.PLayAzan()
                    Window.Zohr_MSG()
            if azan_settings['AzanMaghreb'] and AzanPlayer.state() == QMediaPlayer.State.StoppedState and stopAzanPlayer == False:
                if owghat.Azan_Maghreb == current_time:
                    Window.PLayAzan()
                    Window.Maghreb_MSG()
 
#------------MAIN CLASS------------
class myWindow(QMainWindow, Ui_Owghat, owghat_info):
    # SUPER
    def __init__(self, parent=None):
        super(myWindow, self).__init__(parent)
        self.setupUi(self)
        AzanDataBase = TinyDB(os_dir.DataBase_path)
        self.AllSetting = DataBase.all()[0]
        self.owghat = owghat_info()
        self.path = os_dir()
        self.AzanGoo = AzanGoo()
        self.before = self.AllSetting['reminder']['Before']
        self.TextMSG = f'الان {self.before} قبل از اذان است'
        self.settingdb = DataBase.all()[0]
        Calendar_Pixmap = QPixmap()
        Calendar_Pixmap.loadFromData(self.path.Calendar_path)
        self.trayIcon = SystemTrayIcon(QIcon(Calendar_Pixmap), self)
        self.startup()
        config.read(os_dir.ini)
        self.pixmap = QPixmap()
        self.trayIcon.show()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.RTfunction)
        self.timer.start(1000)
        self.azan_time_remaining = 0

    # close
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # UI
    def initUI(self):
    #------------OTHER------------
        # load city
        region = DataBase.all()[0]
        cityLabel = region["region"]
    #------------FONTS------------
        # font Text
        fontText = QFont()
        fontText.setPointSize(11)
        fontText.setBold(True)
        # font Date
        fontDate = QFont()
        fontDate.setPointSize(9)
        fontDate.setBold(True)
        # hadis Info Font
        hadisInfoFont = QFont()
        hadisInfoFont.setPointSize(11)
        hadisInfoFont.setBold(False)
        # city Font
        cityFont = QFont()
        cityFont.setPointSize(16)
        cityFont.setBold(True)
        # hadis Font
        self.hadisFont = QFont()
        self.hadisFont.setPointSize(9)
        self.hadisFont.setBold(True)

    #------------WIDGETS------------
        # AzanSobhInfo
        self.AzanSobhInfo.setText(self.owghat.Azan_Sobh)
        self.AzanSobhInfo.setFont(fontText)
        # AzanZohr
        self.AzanZohrInfo.setText(self.owghat.Azan_zohr)
        self.AzanZohrInfo.setFont(fontText)
        # AzanMaghreb
        self.AzanMaghrebInfo.setText(self.owghat.Azan_Maghreb)
        self.AzanMaghrebInfo.setFont(fontText)
        # Tolu
        self.ToluInfo.setText(self.owghat.Tolu_Aftab)
        self.ToluInfo.setFont(fontText)
        # Ghorub
        self.GhorubInfo.setText(self.owghat.Ghorub_Aftab)
        self.GhorubInfo.setFont(fontText)
        # NimeShab
        self.NimeShabInfo.setText(self.owghat.Nimeshab)
        self.NimeShabInfo.setFont(fontText)
        # shamsi Date
        self.ShamsiInfo.setText(self.owghat.date_shamsi)
        self.ShamsiInfo.setFont(fontDate)
        self.ShamsiInfo.setAlignment(Qt.AlignmentFlag.AlignRight)
        # ghamari Date
        self.GhamariInfo.setText(self.owghat.date_ghamari)
        self.GhamariInfo.setFont(fontDate)
        self.GhamariInfo.setAlignment(Qt.AlignRight)
        # Miladi Date
        self.MiladiInfo.setText(self.owghat.date_miladi)
        self.MiladiInfo.setFont(fontDate)
        self.MiladiInfo.setAlignment(Qt.AlignRight)
        # Hadis
        self.HadisLabel.setLayoutDirection(Qt.RightToLeft)
        self.HadisLabel.setWordWrap(True)
        self.HadisLabel.setFixedWidth(400)
        self.HadisLabel.setText(self.owghat.hadis_text)
        self.HadisLabel.setFont(self.hadisFont)
        # person Hadis
        self.personLabel.setText(self.owghat.hadis_person)
        self.personLabel.setFont(hadisInfoFont)
        # source Hadis
        self.sourceLabel.setText(self.owghat.hadis_source)
        self.sourceLabel.setFont(hadisInfoFont)
        #city
        self.city.setText(cityLabel)
        self.city.setFont(cityFont)
        #Date Letters
        self.ShamsiLettersInfo.setText(self.owghat.shamsi_letters)
        self.ShamsiLettersInfo.setFont(fontDate)
        self.GhamariLettersInfo.setText(self.owghat.ghamari_letters)
        self.GhamariLettersInfo.setFont(fontDate)
        self.MiladiLettersInfo.setText(self.owghat.miladi_letters)
        self.MiladiLettersInfo.setFont(fontDate)
        #About Me
        self.AboutMe.clicked.connect(self.AboutMe_clicked)
        # setting
        self.setting.clicked.connect(self.setting_clicked)

#------------Update Info------------
    def update(self):
        self.Azandb = TinyDB(os_dir.DataBase_path)
        self.AllAzan = self.Azandb.all()[0]
        self.AzanDataBase = TinyDB(os_dir.DataBase_path)
        self.DataBase = TinyDB(os_dir.DataBaseOS)
        AllSetting = self.DataBase.all()[0]
        city = AllSetting['region']
        self.AllAzandb = self.AzanDataBase.all()[0]
        #apis
        owghat = requests.get(f'http://api.aladhan.com/v1/timingsByCity?city={city}&country=iran&method=7').json()
        self.hadis = requests.get('https://api.keybit.ir/hadis').json()
        
        today_shamsi = jdatetime.date.today()
        today_hijri = convert.Gregorian.today().to_hijri()
        today_gregorian = jdatetime.date.today().togregorian()
        # info owghat
        self.Azan_Sobh_Owghat = owghat['data']['timings']['Fajr']
        self.Azan_zohr_Owghat = owghat['data']['timings']['Dhuhr']
        self.Azan_Maghreb_Owghat = owghat['data']['timings']['Maghrib']
        self.Tolu_Aftab_Owghat = owghat['data']['timings']['Sunrise']
        self.Ghorub_Aftab_Owghat = owghat['data']['timings']['Sunset']
        self.Nimeshab_Owghat = owghat['data']['timings']['Midnight']
        self.date_weekday = today_shamsi.weekday()
        # shamsi
        self.year_shamsi = today_shamsi.year
        self.month_shamsi = today_shamsi.month
        self.day_shamsi = today_shamsi.day
        # hijri
        self.year_hijri = today_hijri.year
        self.month_hijri = today_hijri.month
        self.day_hijri = today_hijri.day
        # gregorian
        self.year_gregorian = today_gregorian.year
        self.month_gregorian = today_gregorian.month
        self.day_gregorian = today_gregorian.day
        self.gregorian_letters = f"{gregorian_weekdays[self.date_weekday]}, {self.day_gregorian} {gregorian_months[self.month_gregorian - 1]}, {self.year_gregorian}"
        self.gregorian = f"{self.year_gregorian}/{self.month_gregorian}/{self.day_gregorian}"
        self.shamsi_letters = f"{shamsi_weekdays[self.date_weekday]}, {self.day_shamsi} {shamsi_months[self.month_shamsi - 1]}, {self.year_shamsi}"
        self.shamsi = f"{self.year_shamsi}/{self.month_shamsi}/{self.day_shamsi}"
        self.hijri_letters = f"{hijri_weekdays[self.date_weekday]}, {self.day_hijri} {hijri_months[self.month_hijri - 1]}, {self.year_hijri}"
        self.hijri = f"{self.year_hijri}/{self.month_hijri}/{self.day_hijri}"
        self.hadis_text_Owghat = self.hadis['result']['text']
        self.hadis_person_Owghat = self.hadis['result']['person']
        self.hadis_source_Owghat = self.hadis['result']['source']
        WeekdaySTR = f"image{self.date_weekday + 1}"
        self.info = self.AzanDataBase.update({
            'weekday': self.date_weekday,
            "shamsi":{'dateshamsi': self.shamsi, "year_shamsi":self.year_shamsi, "month_shamsi":self.month_shamsi, "day_shamsi":self.day_shamsi, "letters": self.shamsi_letters},
            "hijri":{'datehijri': self.hijri, "year_hijri":self.year_hijri, "month_hijri":self.month_hijri, "day_hijri":self.day_hijri, "letters": self.hijri_letters},
            "gregorian":{'dategregorianIso': date.today().isoformat(), 'dategregorian': self.gregorian, "year_gregorian":self.year_gregorian, "month_gregorian":self.month_gregorian, "day_gregorian":self.day_gregorian, "letters": self.gregorian_letters},
            'Hadis': {'Hadis_Text': self.hadis_text_Owghat, 'Hadis_Person': self.hadis_person_Owghat, "Hadis_Source": self.hadis_source_Owghat},
            'iniNumber': WeekdaySTR,
            'AzanSobh': self.Azan_Sobh_Owghat,
            'Azanzohr': self.Azan_zohr_Owghat,
            'AzanMaghreb': self.Azan_Maghreb_Owghat,
            'ToluAftab': self.Tolu_Aftab_Owghat,
            'GhorubAftab': self.Ghorub_Aftab_Owghat,
            'Nimeshab': self.Nimeshab_Owghat
        }, doc_ids=[1])

        self.AzanDataBase2 = TinyDB(os_dir.DataBase_path)
        self.AllAzandb2 = self.AzanDataBase2.all()[0]
        self.Azan_Sobh = self.AllAzandb2['AzanSobh']
        self.Azan_zohr = self.AllAzandb2['Azanzohr']
        self.Azan_Maghreb = self.AllAzandb2['AzanMaghreb']
        self.Tolu_Aftab = self.AllAzandb2['ToluAftab']
        self.Ghorub_Aftab = self.AllAzandb2['GhorubAftab']
        self.Nimeshab = self.AllAzandb2['Nimeshab']
        self.date_shamsi = self.AllAzandb2['shamsi']['dateshamsi']
        self.shamsi_letters = self.AllAzandb2['shamsi']['letters']
        self.date_ghamari = self.AllAzandb2['hijri']['datehijri']
        self.ghamari_letters = self.AllAzandb2['hijri']['letters']
        self.date_miladi = self.AllAzandb2['gregorian']['dategregorian']
        self.miladi_letters = self.AllAzandb2['gregorian']['letters']
        self.hadis_text = self.AllAzandb2['Hadis']['Hadis_Text']
        self.hadis_person = self.AllAzandb2['Hadis']['Hadis_Person']
        self.hadis_source = self.AllAzandb2['Hadis']['Hadis_Source']
        self.iniNumber = self.AllAzandb2['iniNumber']

    # REFRESH WIDGETS
    def refresh(self):
 #------------OTHER------------
        # load city
        region = DataBase.all()[0]
        cityLabel = region["region"]
    #------------FONTS------------
        # font Text
        fontText = QFont()
        fontText.setPointSize(11)
        fontText.setBold(True)
        # font Date
        fontDate = QFont()
        fontDate.setPointSize(9)
        fontDate.setBold(True)
        # hadis Info Font
        hadisInfoFont = QFont()
        hadisInfoFont.setPointSize(11)
        hadisInfoFont.setBold(False)
        # city Font
        cityFont = QFont()
        cityFont.setPointSize(16)
        cityFont.setBold(True)
        # hadis Font
        self.hadisFont = QFont()
        self.hadisFont.setPointSize(9)
        self.hadisFont.setBold(True)

    #------------WIDGETS------------
        # AzanSobhInfo
        self.AzanSobhInfo.setText(self.Azan_Sobh)
        self.AzanSobhInfo.setFont(fontText)
        # AzanZohr
        self.AzanZohrInfo.setText(self.Azan_zohr)
        self.AzanZohrInfo.setFont(fontText)
        # AzanMaghreb
        self.AzanMaghrebInfo.setText(self.Azan_Maghreb)
        self.AzanMaghrebInfo.setFont(fontText)
        # Tolu
        self.ToluInfo.setText(self.Tolu_Aftab)
        self.ToluInfo.setFont(fontText)
        # Ghorub
        self.GhorubInfo.setText(self.Ghorub_Aftab)
        self.GhorubInfo.setFont(fontText)
        # NimeShab
        self.NimeShabInfo.setText(self.Nimeshab)
        self.NimeShabInfo.setFont(fontText)
        # shamsi Date
        self.ShamsiInfo.setText(self.date_shamsi)
        self.ShamsiInfo.setFont(fontDate)
        self.ShamsiInfo.setAlignment(Qt.AlignCenter)
        # ghamari Date
        self.GhamariInfo.setText(self.date_ghamari)
        self.GhamariInfo.setFont(fontDate)
        self.GhamariInfo.setAlignment(Qt.AlignRight)
        # Miladi Date
        self.MiladiInfo.setText(self.date_miladi)
        self.MiladiInfo.setFont(fontDate)
        self.MiladiInfo.setAlignment(Qt.AlignRight)
        # Hadis
        self.HadisLabel.setLayoutDirection(Qt.RightToLeft)
        self.HadisLabel.setWordWrap(True)
        self.HadisLabel.setFixedWidth(400)
        self.HadisLabel.setText(self.hadis_text)
        self.HadisLabel.setFont(self.hadisFont)
        # person Hadis
        self.personLabel.setText(self.hadis_person)
        self.personLabel.setFont(hadisInfoFont)
        # source Hadis
        self.sourceLabel.setText(self.hadis_source)
        self.sourceLabel.setFont(hadisInfoFont)
        #city
        self.city.setText(cityLabel)
        self.city.setFont(cityFont)
        #Date Letters
        self.ShamsiLettersInfo.setText(self.shamsi_letters)
        self.ShamsiLettersInfo.setFont(fontDate)
        self.GhamariLettersInfo.setText(self.ghamari_letters)
        self.GhamariLettersInfo.setFont(fontDate)
        self.MiladiLettersInfo.setText(self.miladi_letters)
        self.MiladiLettersInfo.setFont(fontDate)

#------------Run os Windows------------
    def startup(self):
        if self.AllSetting['Startup']['StartOnWindows'] == True:
            filename, file_extension = os.path.splitext(__file__)
            appformat = "exe"
            if sys.argv[0].endswith('.py'):
                appformat = "py"
            elif sys.argv[0].endswith('.exe'):
                appformat = "exe"
            app_path = f'"{filename}.{appformat}" --StartUp'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'Divine Direction', 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)

        elif self.AllSetting['Startup']['StartOnWindows'] == False:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, 'Divine Direction')
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)

#------------Azan------------
    def PLayAzan(self):
        Moazen = self.AllSetting["Moazen"]
        Azan = os.path.join(self.path.Current_dir, "Azan", Moazen)
        AzanPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(Azan)))
        AzanPlayer.play()
        AzanPlayer.mediaStatusChanged.connect(self.stopAzan)
        
    def stopAzan(self, status):
        if status == QMediaPlayer.EndOfMedia:
            AzanPlayer.stop()

#------------Try Icon Message------------
    def Sobh_MSG(self):
        self.trayIcon.showMessage("وقت اذان", "زمان نماز صبح رسید", QSystemTrayIcon.NoIcon, 15000)
    def Zohr_MSG(self):
        self.trayIcon.showMessage("وقت اذان", "زمان نماز ظهر رسید", QSystemTrayIcon.NoIcon, 15000)
    def Maghreb_MSG(self):
        self.trayIcon.showMessage("وقت اذان", "زمان نماز مغرب رسید", QSystemTrayIcon.NoIcon, 15000)

    def new_Sobh_msg(self):
        self.trayIcon.showMessage("یاداوری اذان صبح", self.TextMSG, QSystemTrayIcon.NoIcon, 1500)
    def new_zohr_msg(self):
        self.trayIcon.showMessage("یاداوری اذان ظهر", self.TextMSG, QSystemTrayIcon.NoIcon, 15000)
    def new_Maghreb_msg(self):
        self.trayIcon.showMessage("یاداوری اذان مغرب", self.TextMSG, QSystemTrayIcon.NoIcon, 15000)

    def RTfunction(self):
        if self.azan_time_remaining > 0:
            self.azan_time_remaining -= 1
            return

        fontText = QFont()
        fontText.setPointSize(11)
        fontText.setBold(True)
        current_time = QTime.currentTime()
        azan_times = {
            "AzanSobhInfo": QTime.fromString(self.AzanSobhInfo.text(), 'hh:mm'),
            "AzanZohrInfo": QTime.fromString(self.AzanZohrInfo.text(), 'hh:mm'),
            "AzanMaghrebInfo": QTime.fromString(self.AzanMaghrebInfo.text(), 'hh:mm')
        }

        azan_names = {
            "AzanSobhInfo": "صبح",
            "AzanZohrInfo": "ظهر",
            "AzanMaghrebInfo": "مغرب"
        }

        future_azan_times = [azan_time for azan_time in azan_times.values() if azan_time > current_time]
        
        if not future_azan_times:
            next_azan = azan_times["AzanSobhInfo"].addSecs(24*60*60)
            next_azan_label = "AzanSobhInfo"
        else:
            next_azan = min(future_azan_times)
            next_azan_label = [label for label, time in azan_times.items() if time == next_azan][0]

        remaining_seconds = current_time.secsTo(next_azan)
        if remaining_seconds < 0:
            remaining_seconds += 24*60*60

        hours, remainder = divmod(remaining_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours == 0 and minutes == 0 and seconds <= 2:
            self.RemainingTime.setText(f"الان اذان {azan_names[next_azan_label]} است")
            self.azan_time_remaining = 60
        else:
            remaining_time_parts = []
            if hours > 0:
                remaining_time_parts.append(f"{hours} ساعت")
            if minutes > 0 or hours > 0:
                remaining_time_parts.append(f"{minutes} دقیقه")
            remaining_time_parts.append(f"{seconds} ثانیه")
            remaining_time_str = " و ".join(remaining_time_parts)

            self.RemainingTime.setText(f"{remaining_time_str} تا اذان {azan_names[next_azan_label]}")

        self.RemainingTime.setFont(fontText)
        self.RemainingTime.setAlignment(Qt.AlignCenter)



#------------CONNECTION------------
    @pyqtSlot()
    def AboutMe_clicked(self):
        dialog = AboutDialog()
        dialog.exec_()

    @pyqtSlot()
    def setting_clicked(self):
        global lineEditChanged__Variable, Cancel_clicked_Variable
        dialog = SettingDialog(self)
        dialog.exec_()
        if lineEditChanged__Variable == True and Cancel_clicked_Variable == False:
            owghat_info()
            self.update()
            self.startup()
            self.refresh()
            lineEditChanged__Variable = False

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        fontText = QFont()
        fontText.setPointSize(9)
        fontText.setBold(True)

        self.setWindowTitle("درباره سازنده")
        self.setWindowIcon(QIcon(os_dir.AboutMe_path))
        self.resize(410, 230)

        layout = QVBoxLayout()

        text = QLabel()
        text.setText("اسم این برنامه Divine Direction می باشد نسخه اولیه این برنامه در تاریخ 1402/6/22 ساعت 18:00 با زبان پایتون نوشته شد سازنده ی این برنامه اقای محمد عرفان کولیوند میباشد. هرگونه کپی برداری با نوشتن کپی رایت بلاک در سورس کد و در برنامه (چه به صورت کنسولی و چه به صورت برنامه ی دارای رابط گرافیکی) و ایمیل دادن به ایمیل پشتیبانی برنامه مجاز می باشد و در صورت ننوشتن کپی رایت بلاک مجبور  به شکایت کردن از شما هستم.")
        text.setLayoutDirection(Qt.RightToLeft)
        text.setWordWrap(True)
        text.setFixedWidth(500)
        text.setFont(fontText)
        layout.addWidget(text)
        
        Spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(Spacer)

        copyright = QLabel()
        copyright.setText('کپی رایت بلاک:\n "برای ساخت این برنامه از برنامه دیگری به اسم Divine Direction استفاده شده است"')
        copyright.setFont(fontText)
        layout.addWidget(copyright)

        email = QLabel()
        email.setText('<a href="mailto:erfan1221kolivand@gmail.com">erfan1221kolivand@gmail.com</a>')
        email.setOpenExternalLinks(True)
        email.setAlignment(Qt.AlignmentFlag.AlignRight)
        email.setFont(fontText)
        layout.addWidget(email)

        self.setLayout(layout)

#------------Setting------------
class SettingDialog(QDialog, Ui_Setting):
    def __init__(self, parent=None):
        super(SettingDialog, self).__init__(parent)
        self.setupUi(self)
        self.dir_path = os_dir()
        self.azan()
        self.State()
        self.UI_dialog()
        self.compeleter()
 
    def azan(self):
        folder_path = self.dir_path.combobox
        for filename in os.listdir(folder_path):
            if filename.endswith('.mp3') or filename.endswith('.wav') or filename.endswith('.aac') or filename.endswith('.flac') or filename.endswith('.m4a') or filename.endswith('.ogg') or filename.endswith('.wma'):
                name, ext = os.path.splitext(filename)
                self.Moazen.addItem(name)

    def compeleter(self):
        self.cities = []

        for file in ["bakhsh.csv", "dehestan.csv", "ostan.csv", "shahr.csv", "shahrestan.csv"]:
            file_path = os.path.join(self.dir_path.data_path, file)
            df = pd.read_csv(file_path)
            for city in df["name"].tolist():
                if not city[-1].isdigit():
                    self.cities.append(city)
        self.cities = list(set(self.cities))

        completer = QCompleter(self.cities)
        self.lineEdit.setCompleter(completer)

    def State(self):
        settings = DataBase.all()[0]
        # Azan
        self.AzanSobh.setChecked(settings["Azan"]['AzanSobh'])
        self.AzanZohr.setChecked(settings["Azan"]['AzanZohr'])
        self.AzanMaghreb.setChecked(settings["Azan"]['AzanMaghreb'])
        # Combo box
        name, ext = os.path.splitext(settings['Moazen'])
        moazen_index = self.Moazen.findText(name)
        if moazen_index != -1:
            self.Moazen.setCurrentIndex(moazen_index)
        # Time Edit
        reminder_time = settings["reminder"]["Before"]
        time = QTime.fromString(reminder_time, "hh:mm")
        self.TimeEdit.setTime(time)
        # PlayReminderAzan
        self.PlayReminderAzan.setChecked(settings["reminder"]['remindercheckBox'])
        reminder_enabled = settings["reminder"]["remindercheckBox"]
        self.TimeEdit.setEnabled(reminder_enabled)
        #ُ StartOnWindows
        self.StartOnWindowsBTN.setChecked(settings['Startup']["StartOnWindows"])
        # LineEdit
        self.lineEdit.setText(settings["region"])

        if settings["OfflineMode"] == True and settings["restart"] == False:
            self.Save.setText("ذخیره (نیازمند به بازنشانی)")
        elif settings["OfflineMode"] == False:
            self.Save.setText("ذخیره")

    def UI_dialog(self):
        #Connection
        self.PlayAzan.clicked.connect(self.PlayAzan_Clicked)
        mediaPlayer.mediaStatusChanged.connect(self.PlayAzan_state)
        self.OpnFolder.clicked.connect(self.OpnFolder_Clicked)
        self.Save.clicked.connect(self.Save_Clicked)
        self.PlayReminderAzan.stateChanged.connect(self.Reminder_stateChanged)
        self.offlineMode.stateChanged.connect(self.offlineMode_stateChanged)
        self.offlineMode.stateChanged.connect(self.Save_Text)
        self.Cancel.clicked.connect(self.Cancel_clicked)
        self.lineEdit.textChanged.connect(self.on_text_changed)
        self.offlineMode.hide()        

    def on_text_changed(self):
        global lineEditChanged__Variable
        lineEditChanged__Variable = True
        self.offlineMode.setChecked(False)
        self.offlineMode.setEnabled(False)

    def PlayAzan_Clicked(self):
        if self.PlayAzan.text() == 'پخش اذان':
            self.PlayAzan.setText('متوقف کردن')
            selected_file = self.Moazen.currentText()
            for ext in ['.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg', '.wma']:
                file_path = os.path.join(self.dir_path.combobox, selected_file + ext)
                if os.path.exists(file_path):
                    mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
                    mediaPlayer.play()
                    break
        else:
            mediaPlayer.stop()
            self.PlayAzan.setText('پخش اذان')

    def PlayAzan_state(self):
        if mediaPlayer == mediaPlayer.MediaStatus.EndOfMedia:
            mediaPlayer.stop()

    def OpnFolder_Clicked(self):
        os.startfile(self.dir_path.combobox)

    def Cancel_clicked(self):
        global Cancel_clicked_Variable
        mediaPlayer.stop()
        Cancel_clicked_Variable = True
        self.reject()

    def Save_Clicked(self):
        global SettingDialogClose

        mediaPlayer.stop()
        # value
        azan_sobh_value = self.AzanSobh.isChecked()
        Azan_Maghreb_value = self.AzanMaghreb.isChecked()
        Azan_Zohr_value = self.AzanZohr.isChecked()
        # Azan
        DataBase.update({"Azan": {"AzanSobh": azan_sobh_value, "AzanZohr": Azan_Zohr_value, "AzanMaghreb": Azan_Maghreb_value}}, Query().Azan.exists(), doc_ids=[1])

        # PlayReminderAzan
        PlayReminderAzan_value = self.PlayReminderAzan.isChecked()
        TimeEdit = self.TimeEdit.time()
        TimeEditStr = TimeEdit.toString("hh:mm")
        DataBase.update({"reminder": {"remindercheckBox": PlayReminderAzan_value, "Before": TimeEditStr}}, Query().reminder.exists(), doc_ids=[1])

        # StartOnWindows
        StartOnWindowsBTN_value = self.StartOnWindowsBTN.isChecked()
        DataBase.update({"Startup":{"StartOnWindows": StartOnWindowsBTN_value}}, doc_ids=[1])

        # Combobox
        selected_file = self.Moazen.currentText()
        for ext in ['.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg', '.wma']:
            file_path = os.path.join(self.dir_path.combobox, selected_file + ext)
            if os.path.exists(file_path):
                DataBase.update({'Moazen': selected_file + ext}, doc_ids=[1])
                break
        
        OfflineMode_value = self.offlineMode.isChecked()
        DataBase.update({"OfflineMode": OfflineMode_value})
        if OfflineMode_value == False:
            DataBase.update({"restart": False})

        # LineEdit
        city = self.lineEdit.text()
        if city in self.cities:
            LineEdit_Text = self.lineEdit.text()
            DataBase.update({"region": LineEdit_Text}, doc_ids=[1])
            SettingDialogClose = True
        else:
            QMessageBox.warning(self, "خطا", "شهری که انتخاب کردیت نامعتبر است")
            SettingDialogClose = None

        settings = DataBase.all()[0]
        if settings["OfflineMode"] == True and settings["restart"] == False and SettingDialogClose == True:
            QApplication.quit()
            DataBase.update({"restart": True})
            os.execl(sys.executable, sys.executable, *sys.argv)
        elif SettingDialogClose == True:
            self.accept()

    def offlineMode_stateChanged(self, state):
        if state == Qt.Checked:
            self.lineEdit.setEnabled(False)
            self.label.setEnabled(False)
            self.groupBox.setEnabled(False)
        else:
            self.lineEdit.setEnabled(True)
            self.label.setEnabled(True)
            self.groupBox.setEnabled(True)

    def Save_Text(self, state):
        if state == Qt.Checked:
            self.Save.setText("ذخیره (نیازمند به بازنشانی)")
        else:
            self.Save.setText("ذخیره")

    def Reminder_stateChanged(self, state):
        if state == Qt.Checked:
            self.TimeEdit.setEnabled(True)
            self.ReminderLabel.setEnabled(True)
            self.ReminderLabel2.setEnabled(True)
        else:
            self.TimeEdit.setEnabled(False)
            self.ReminderLabel.setEnabled(False)
            self.ReminderLabel2.setEnabled(False)

    def close_function(self):
        global SettingDialogClose
        settings = DataBase.all()[0]
        if settings["OfflineMode"] == True and settings["restart"] == False and SettingDialogClose == True:
            QApplication.quit()
            DataBase.update({"restart": True})
            os.execl(sys.executable, sys.executable, *sys.argv)
        elif SettingDialogClose == True:
            self.accept()

#------------SystemTrayIcon------------
class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        QFontDatabase.addApplicationFont(os_dir.font2)
        font = QFont('Vazir', 10)
        font.setBold(False)
        menu.setFont(font)
        self.openAction = menu.addAction("بستن برنامه")
        self.stopAction = menu.addAction("متوقف کردن")
        exitAction = menu.addAction("خروج")
        self.stopAction.setEnabled(False)
        self.setContextMenu(menu)
        exitAction.triggered.connect(self.exit)
        self.activated.connect(self.iconActivated)
        self.stopAction.triggered.connect(self.stop)
        self.openAction.triggered.connect(self.open)
        AzanPlayer.mediaStatusChanged.connect(self.state)

    def state(self):
        if AzanPlayer.state() == QMediaPlayer.PlayingState:
            self.stopAction.setEnabled(True)

        else:
            self.stopAction.setEnabled(False)

    def stop(self):
        global stopAzanPlayer
        AzanPlayer.stop()
        stopAzanPlayer = True

    def exit(self):
        self.AzanGoo = AzanGoo()
        self.AzanGoo.myTimer.stop()
        QApplication.quit()

    def open(self):
        if self.parent().isHidden():
            self.openAction.setText("بستن برنامه")
            self.parent().show()
            self.stopAction.setEnabled(True)
        else:
            self.openAction.setText("باز کردن")
            self.parent().hide()
            self.stopAction.setEnabled(True)

    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.parent().isHidden():
                self.parent().show()
            else:
                self.parent().hide()

#------------EXECT------------
def window():
    app = QApplication(sys.argv)
    win = myWindow()
    if '--StartUp' in sys.argv:
        win.hide()
    else:
        win.show()
    QFontDatabase.addApplicationFont(os_dir.font)
    font = QFont('Vazir', 10)
    font.setBold(False)
    app.setFont(font)
    sys.exit(app.exec_())

if __name__ == '__main__':
    window()
