import sys
import os
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Design.ui', self)
        self.delta_ind = 0
        self.delta_pars = [0.5, 1, 2, 4, 6, 10, 18, 70]
        self.image = QLabel(self)
        self.image.move(0, 100)
        self.image.resize(600, 450)

        self.pushButton_sql.clicked.connect(lambda: self.set_view('skl'))
        self.pushButton_sat.clicked.connect(lambda: self.set_view('sat'))
        self.pushButton_map.clicked.connect(lambda: self.set_view('map'))

        self.btn_search.clicked.connect(lambda: self.search_object(self.line_search.text()))
        self.pushButton_reset.clicked.connect(self.reset_pt)

        self.lon = 37.530887
        self.lat = 55.703118
        self.move_speed = 0.001
        self.view = 'map'
        self.addr = ''
        self.default_addr = 'Поле для адресса выбранной метки'

        self.pt = False
        self.pt_params = ""

        self.add_img()
    
    def set_addr_label(self):
        self.label_addr.setText(self.addr)

    def set_view(self, arg):
        self.view = arg
        self.add_img()

    def add_img(self):
        api_server = "http://static-maps.yandex.ru/1.x/"

        self.params = {
            "ll": ",".join([str(self.lon), str(self.lat)]),
            "spn": ",".join([str(self.delta_pars[self.delta_ind] / 100), str(self.delta_pars[self.delta_ind] / 100)]),
            "l": self.view
        }

        if self.pt:
            self.params["pt"] = self.pt_params

        try:
            response = requests.get(api_server, params=self.params)
        except:
            response = None

        if response:
            f = open("Res.png", 'wb')
            data = response.content
            f.write(data)
            self.pixmap = QPixmap('Res.png')
            self.image.setPixmap(self.pixmap)
            f.close()
            os.remove('Res.png')

    def reset_pt(self):
        self.pt = False
        self.addr = self.default_addr
        self.set_addr_label()
        self.add_img()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_PageUp, Qt.Key_1]:
            self.change_delta(False)
        if event.key() in [Qt.Key_PageDown, Qt.Key_2]:
            self.change_delta(True)
        if event.key() == Qt.Key_A:
            self.lon -= self.move_speed
            self.add_img()
        if event.key() == Qt.Key_W:
            self.lat += self.move_speed
            self.add_img()
        if event.key() == Qt.Key_D:
            self.lon += self.move_speed
            self.add_img()
        if event.key() == Qt.Key_S:
            self.lat -= self.move_speed
            self.add_img()

    def change_delta(self, arg):
        if arg:
            if self.delta_ind < 7:
                self.move_speed *= 2
                self.delta_ind += 1
                self.add_img()
        else:
            if self.delta_ind > 0:
                self.move_speed /= 2
                self.delta_ind -= 1
                self.add_img()

    def search_object(self, param):
        try:
            response = requests.get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b"
                                    f"&geocode={param}&format=json")
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            self.addr = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            self.set_addr_label()
            self.lon, self.lat = float(toponym_coodrinates.split(' ')[0]), float(toponym_coodrinates.split(' ')[1])
            self.pt = True
            self.pt_params = f"{self.lon},{self.lat},pm2gnl"
            self.add_img()
        except:
            error = QMessageBox(self)
            error.setText('Такого объекта не существует')
            error.exec()
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
