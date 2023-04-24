import RS485
from multiprocessing import Process, Manager
import time
from mainwindow import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import datetime
import sql_select
from scipy import signal
import scipy.io as sio
from scipy.fft import fft, fftfreq
import numpy as np


class DemoMain(QMainWindow, Ui_MainWindow):
    def __init__(self, shared_data):
        # 初始化父类
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.shared_data = shared_data
        self.stackedWidget.setMaximumHeight(900)
        self.showMaximized()
        self.init()

        #self.showMaximized()
        # self.comboBox.currentIndexChanged.connect(self.updateplot)
        # self.comboBox_2.currentIndexChanged.connect(self.updateplot_2)
        # self.comboBox_3.currentIndexChanged.connect(self.updateplot_3)

        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.comboBox.activated.connect(self.stackedChanged)
        # self.showMaximized()
        # 定时器，定时更新数据
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.updateData)

        # plot初始化
        self.timer1 = QTimer()
        self.timer1.setInterval(200)
        self.timer1.timeout.connect(self.update_plotdata)

        self.timer2 = QTimer()
        self.timer2.setInterval(200)
        self.timer2.timeout.connect(self.update_plotdata_1024)

        self.timer.start()  # 1000=1s
        self.timer1.start()


    def init(self):
        ls = ['x轴振动速度RMS平均值', 'y轴振动速度RMS平均值', 'z轴振动速度RMS平均值', 'x轴振动加速度RMS平均值', 'y轴振动加速度RMS平均值', 'z轴振动加速度RMS平均值',
              'x轴振动速度最大值–峰值', 'x轴振动速度峭度平均值', 'x轴振动加速度最大值-峰值', 'x轴振动加速度峭度平均值', 'y轴振动速度最大值–峰值', 'y轴振动速度峭度平均值',
              'y轴振动加速度最大值-峰值', 'y轴振动加速度峭度平均值', 'z轴振动速度最大值–峰值', 'z轴振动速度峭度平均值', 'z轴振动加速度最大值-峰值', 'z轴振动加速度峭度平均值',
              'x轴振动位移峰峰值', 'y轴振动位移峰峰值', 'z轴振动位移峰峰值', ]

        # 22,[23,62][63,102,][103,142]'频谱分析周期计数',
        ls_2 = ['振动通道 ID', '该测点转速', '内圈特征值 1X', '外圈特征值 1X', '滚动体特征 1X', '保持架特征值 1X', '关注点1加速度谱能量',
                '关注点2加速度谱能量',
                '关注点3加速度谱能量', '关注点4加速度谱能量', '关注点5加速度谱能量', '关注点6加速度谱能量', '关注点7加速度谱能量', '关注点8加速度谱能量', '关注带1加速度谱能量',
                '关注带2加速度谱能量',
                '关注带3加速度谱能量', '关注带4加速度谱能量', '关注带5加速度谱能量', '加速度谱最高能量点的阶次', '加速度谱总能量', '叶片特征值 1X', '叶片特征值 2X', '叶片特征值 3X',
                '叶片特征值 4X', '关注点1速度谱能量', '关注点2速度谱能量', '关注点3速度谱能量', '关注点4速度谱能量', '关注点5速度谱能量', '关注点6速度谱能量', '关注点7速度谱能量',
                '关注点8速度谱能量', '关注带1速度谱能量', '关注带2速度谱能量', '关注带3速度谱能量', '关注带4速度谱能量', '关注带5速度谱能量', '速度谱最高能量点的阶次', '速度谱总能量',
                '振动通道 ID',
                '该测点转速', '内圈特征值 1X', '外圈特征值 1X', '滚动体特征 1X', '保持架特征值 1X', '关注点1加速度谱能量', '关注点2加速度谱能量', '关注点3加速度谱能量',
                '关注点4加速度谱能量',
                '关注点5加速度谱能量', '关注点6加速度谱能量', '关注点7加速度谱能量', '关注点8加速度谱能量', '关注带1加速度谱能量', '关注带2加速度谱能量', '关注带3加速度谱能量',
                '关注带4加速度谱能量',
                '关注带5加速度谱能量', '加速度谱最高能量点的阶次', '加速度谱总能量', '叶片特征值 1X', '叶片特征值 2X', '叶片特征值 3X', '叶片特征值 4X', '关注点1速度谱能量',
                '关注点2速度谱能量',
                '关注点3速度谱能量', '关注点4速度谱能量', '关注点5速度谱能量', '关注点6速度谱能量', '关注点7速度谱能量', '关注点8速度谱能量', '关注带1速度谱能量', '关注带2速度谱能量',
                '关注带3速度谱能量', '关注带4速度谱能量', '关注带5速度谱能量', '速度谱最高能量点的阶次', '速度谱总能量', '振动通道 ID', '该测点转速', '内圈特征值 1X',
                '外圈特征值 1X',
                '滚动体特征 1X', '保持架特征值 1X', '关注点1加速度谱能量', '关注点2加速度谱能量', '关注点3加速度谱能量', '关注点4加速度谱能量', '关注点5加速度谱能量',
                '关注点6加速度谱能量',
                '关注点7加速度谱能量', '关注点8加速度谱能量', '关注带1加速度谱能量', '关注带2加速度谱能量', '关注带3加速度谱能量', '关注带4加速度谱能量', '关注带5加速度谱能量',
                '加速度谱最高能量点的阶次',
                '加速度谱总能量', '叶片特征值 1X', '叶片特征值 2X', '叶片特征值 3X', '叶片特征值 4X', '关注点1速度谱能量', '关注点2速度谱能量', '关注点3速度谱能量',
                '关注点4速度谱能量',
                '关注点5速度谱能量', '关注点6速度谱能量', '关注点7速度谱能量', '关注点8速度谱能量', '关注带1速度谱能量', '关注带2速度谱能量', '关注带3速度谱能量', '关注带4速度谱能量',
                '关注带5速度谱能量', '速度谱最高能量点的阶次', '速度谱总能量']

        self.comboBox.addItem('振动温度一体传感器时域数据')
        self.comboBox.addItem('振动温度一体传感器谱分析数据')
        self.comboBox.addItem('振动温度一体传感器分析图')

        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(12)
        # self.tableWidget.setHorizontalHeaderLabels(['名称1', '数值1'])
        row = 0
        col = 0
        for i in range(len(ls)):
            item = QtWidgets.QTableWidgetItem(ls[i])
            self.tableWidget.setItem(row, col, item)
            if col == 4 or col == 6 or col == 8:
                if row < 3:
                    row += 1
                else:
                    row = 0
                    col += 2
            else:
                if row < 2:
                    row += 1
                else:
                    row = 0
                    col += 2

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)  # 行列序号取消
        self.tableWidget.resizeColumnsToContents()  # 根据内容调整列宽
        # self.tableWidget.resizeRowsToContents()#根据内容调整行高
        self.tableWidget.setFixedHeight(150)
        # self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(100)

        # self.tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.stackedWidget.resize(800, 1200)

        # self.stackedWidget.removeWidget(self.stackedWidget.widget(0))  # 删除页面0
        # self.stackedWidget.removeWidget(self.stackedWidget.widget(0))  # 删除页面1
        # self.stackedWidget.addWidget(self.tableWidget)
        # self.stackedWidget.setCurrentIndex(2)
        # self.tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.tableWidget_2.setRowCount(20)
        self.tableWidget_2.setColumnCount(12)
        # self.tableWidget.setHorizontalHeaderLabels(['名称1', '数值1'])
        row = 0
        col = 0
        for i in range(len(ls_2)):
            item = QtWidgets.QTableWidgetItem(ls_2[i])
            self.tableWidget_2.setItem(row, col, item)
            if row < 19:
                row += 1
            else:
                row = 0
                col += 2
        self.tableWidget_2.verticalHeader().setVisible(False)
        self.tableWidget_2.horizontalHeader().setVisible(False)  # 行列序号取消
        self.tableWidget_2.resizeColumnsToContents()  # 根据内容调整列宽
        # self.tableWidget.resizeRowsToContents()#根据内容调整行高
        self.tableWidget_2.setFixedHeight(800)
        # self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.horizontalHeader().setMinimumSectionSize(100)

        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget()
        self.plot_2 = pg.PlotWidget()
        self.plot_3 = pg.PlotWidget()
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().addWidget(self.plot)
        self.widget_2.setLayout(QtWidgets.QVBoxLayout())
        self.widget_2.layout().addWidget(self.plot_2)
        self.widget_3.setLayout(QtWidgets.QVBoxLayout())
        self.widget_3.layout().addWidget(self.plot_3)

        # self.plot_4 = pg.PlotWidget()
        # self.plot_5 = pg.PlotWidget()
        # self.plot_6 = pg.PlotWidget()

        self.plot_7 = pg.PlotWidget()
        self.plot_8 = pg.PlotWidget()

        self.plot_9 = pg.PlotWidget()
        self.plot_10 = pg.PlotWidget()
        self.plot_11 = pg.PlotWidget()
        self.plot_12 = pg.PlotWidget()
        self.plot_13 = pg.PlotWidget()
        self.plot_14 = pg.PlotWidget()

        # self.widget_4.setLayout(QtWidgets.QVBoxLayout())
        # self.widget_4.layout().addWidget(self.plot_4)
        # self.widget_5.setLayout(QtWidgets.QVBoxLayout())
        # self.widget_5.layout().addWidget(self.plot_5)
        # self.widget_6.setLayout(QtWidgets.QVBoxLayout())
        # self.widget_6.layout().addWidget(self.plot_6)
        self.widget_7.setLayout(QtWidgets.QVBoxLayout())
        self.widget_7.layout().addWidget(self.plot_7)
        self.widget_8.setLayout(QtWidgets.QVBoxLayout())
        self.widget_8.layout().addWidget(self.plot_8)

        self.widget_9.setLayout(QtWidgets.QVBoxLayout())
        self.widget_9.layout().addWidget(self.plot_9)
        self.widget_10.setLayout(QtWidgets.QVBoxLayout())
        self.widget_10.layout().addWidget(self.plot_10)
        self.widget_11.setLayout(QtWidgets.QVBoxLayout())
        self.widget_11.layout().addWidget(self.plot_11)
        self.widget_12.setLayout(QtWidgets.QVBoxLayout())
        self.widget_12.layout().addWidget(self.plot_12)
        self.widget_13.setLayout(QtWidgets.QVBoxLayout())
        self.widget_13.layout().addWidget(self.plot_13)
        self.widget_14.setLayout(QtWidgets.QVBoxLayout())
        self.widget_14.layout().addWidget(self.plot_14)

        # self.plot.plot(self.x, self.y, pen=pg.mkPen('b', width=2))
        # 设置 x 轴范围为 0-3000毫秒，y 轴范围为 0-10
        self.plot.setRange(xRange=[0, 3000], yRange=[0, 50])
        # 设置时间轴单位为毫秒
        self.plot.setLabel('bottom', 'Time', units='ms')
        self.plot_2.setRange(xRange=[0, 3000], yRange=[0, 50])
        # 设置时间轴单位为毫
        self.plot_2.setLabel('bottom', 'Time', units='ms')
        self.plot_3.setRange(xRange=[0, 3000], yRange=[0, 50])
        # 设置时间轴单位为毫秒
        self.plot_3.setLabel('bottom', 'Time', units='ms')

        # self.label_7.setStyleSheet("QLabel { background-color: #FFC0CB; color: black; text-shadow: 1px 1px #000000; }")

        # self.label.setStyleSheet(
        #     "QLabel {background-color: #696969; color: #333333; border: 1px solid #A9A9A9; padding: 5px;}")
        # background-color 表示背景颜色，color 表示字体颜色，border 表示边框样式和颜色，padding 表示文本与边框的距离
        self.comboBox_2.addItem('x轴振动速度')
        self.comboBox_2.addItem('x轴振动加速度')
        self.comboBox_2.addItem('x轴位移')
        self.comboBox_3.addItem('y轴振动速度')
        self.comboBox_3.addItem('y轴振动加速度')
        self.comboBox_3.addItem('y轴位移')
        self.comboBox_4.addItem('z轴振动速度')
        self.comboBox_4.addItem('z轴振动加速度')
        self.comboBox_4.addItem('z轴位移')

        self.comboBox_5.addItem('三轴时域')
        self.comboBox_5.addItem('三轴频域')

        self.pushButton.setText('Select File')
        self.pushButton.clicked.connect(self.showFileDialog)


    def stackedChanged(self, index):
        if index == 0:
            self.timer2.stop()
            self.timer1.start()
            self.stackedWidget.setCurrentIndex(0)
            temp = self.shared_data['flag']
            temp[0] = 0
            self.shared_data['flag'] = temp
        elif index == 1:
            self.timer2.stop()
            self.timer1.stop()
            self.stackedWidget.setCurrentIndex(1)
            temp = self.shared_data['flag']
            temp[0] = 1
            self.shared_data['flag'] = temp
        elif index == 2:
            self.timer.stop()
            self.timer1.stop()
            self.stackedWidget.setCurrentIndex(2)
            temp = self.shared_data['flag']
            temp[0] = 2
            self.shared_data['flag'] = temp
            self.timer2.start()

    def tabChanged(self, index):
        if index == 0:
            self.timer1.start()

        elif index == 1:
            self.timer1.stop()


    def updateData(self):
        # if len(self.shared_data['shard'])>=20:
        if self.stackedWidget.currentIndex() == 0:
            if type(self.shared_data['shard']) == list:
                row = 0
                col = 1
                for i in range(22):
                    if i == 3:
                        pass
                    else:
                        item = QtWidgets.QTableWidgetItem(str(self.shared_data['shard'][i]))
                        self.tableWidget.setItem(row, col, item)
                        #print(row, col, item)
                        if col == 5 or col == 7 or col == 9:
                            if row < 3:
                                row += 1
                            else:
                                row = 0
                                col += 2
                        else:
                            if row < 2:
                                row += 1
                            else:
                                row = 0
                                col += 2

        elif self.stackedWidget.currentIndex() == 1:
            #print(1)
            if type(self.shared_data['shard']) == list:
                row = 0
                col = 1
                for i in range(len(self.shared_data['shard'])):
                    item = QtWidgets.QTableWidgetItem(str(self.shared_data['shard'][i]))
                    self.tableWidget_2.setItem(row, col, item)
                    #print(row, col, item)
                    if row < 19:
                        row += 1
                    else:
                        row = 0
                        col += 2

    def update_plotdata(self):
        xtext = self.comboBox_2.currentText()
        ytext = self.comboBox_3.currentText()
        ztext = self.comboBox_4.currentText()
        if xtext == 'x轴振动速度':
            xi = 2
        if xtext == 'x轴振动加速度':
            xi = 5
        if xtext == 'x轴位移':
            xi = 8
        if ytext == 'y轴振动速度':
            yi = 3
        if ytext == 'y轴振动加速度':
            yi = 6
        if ytext == 'y轴位移':
            yi = 9
        if ztext == 'z轴振动速度':
            zi = 4
        if ztext == 'z轴振动加速度':
            zi = 7
        if ztext == 'z轴位移':
            zi = 10

        now = datetime.datetime.now()
        xdata, xtime = sql_select.getdate(now, xi)
        ydata, ytime = sql_select.getdate(now, yi)
        zdata, ztime = sql_select.getdate(now, zi)
        if xdata == []:
            pass
        else:
            # # 平滑处理
            # window_size = 7
            # order = 3
            #
            # if len(xdata) > window_size:
            #     xdata = savgol_filter(xdata, window_size, order)
            #     N = len(xdata)
            #     T = 0.2
            #     yf = fft(xdata)
            #     xf = fftfreq(N, T)[:N // 2]
                # t_new = np.linspace(xtime[0], xtime[-1], 1000)
                # x_resampled = np.interp(t_new, xtime, xdata)
                #
                # N = len(x_resampled)
                # T = t_new[1] - t_new[0]
                # yf = fft(x_resampled)
                # xf = fftfreq(N, T)[:N // 2]

                # for item in self.plot_4.items():
                #     if isinstance(item, pg.TextItem):
                #         self.plot_4.removeItem(item)
                # self.plot_4.clearPlots()
                # # 20 * np.log10(2.0 / N * np.abs(yf[:N // 2]))
                # self.plot_4.plot(xf, 2.0 / N * np.abs(yf[:N // 2]), pen=pg.mkPen(pg.intColor(0), width=2))
                # self.plot_4.autoRange()
                # self.plot_4.setRange(xRange=[1, np.max(xf)],yRange=[0.01, 10])
            # else:
            #     if len(xdata)%2!=0:
            #         xdata = savgol_filter(xdata, len(xdata), order)
            #     else:
            #         xdata = savgol_filter(xdata, len(xdata)-1, order)
            #
            # if len(ydata) > window_size:
            #     ydata = savgol_filter(ydata, window_size, order)
            #     N = len(ydata)
            #     T = 0.2
            #     yf = fft(ydata)
            #     xf = fftfreq(N, T)[:N // 2]
            #
            #     for item in self.plot_5.items():
            #         if isinstance(item, pg.TextItem):
            #             self.plot_5.removeItem(item)
            #     self.plot_5.clearPlots()
            #
            #     self.plot_5.plot(xf, 2.0 / N * np.abs(yf[:N // 2]), pen=pg.mkPen(pg.intColor(0), width=2))
            #     self.plot_5.autoRange()
            #
            # if len(zdata) > window_size:
            #     zdata = savgol_filter(zdata, window_size, order)
            #     N = len(zdata)
            #     T = 0.2
            #     yf = fft(zdata)
            #     xf = fftfreq(N, T)[:N // 2]
            #
            #     for item in self.plot_6.items():
            #         if isinstance(item, pg.TextItem):
            #             self.plot_6.removeItem(item)
            #     self.plot_6.clearPlots()
            #
            #     self.plot_6.plot(xf, 2.0 / N * np.abs(yf[:N // 2]), pen=pg.mkPen(pg.intColor(0), width=2))
            #     self.plot_6.autoRange()
            # xdata=np.array(xdata)
            # xtime=np.array(xtime)
            for item in self.plot.items():
                if isinstance(item, pg.TextItem):
                    self.plot.removeItem(item)
            self.plot.clearPlots()

            for item in self.plot_2.items():
                if isinstance(item, pg.TextItem):
                    self.plot_2.removeItem(item)
            self.plot_2.clearPlots()

            for item in self.plot_3.items():
                if isinstance(item, pg.TextItem):
                    self.plot_3.removeItem(item)
            self.plot_3.clearPlots()

            self.plot.plot(xtime, xdata, pen=pg.mkPen(pg.intColor(0), width=2),
                           symbol='o', symbolSize=2)
            self.plot.autoRange()
            self.plot.setRange(xRange=[0, 30000])
            self.plot_2.plot(ytime, ydata, pen=pg.mkPen(pg.intColor(0), width=2),
                             symbol='o', symbolSize=2)
            self.plot_2.autoRange()
            self.plot_2.setRange(xRange=[0, 30000])
            self.plot_3.plot(ztime, zdata, pen=pg.mkPen(pg.intColor(0), width=2),
                             symbol='o', symbolSize=2)
            self.plot_3.autoRange()
            self.plot_3.setRange(xRange=[0, 30000])

    def update_plotdata_1024(self):
        if len(self.shared_data['shard']) == 3:
            lst = [i for i in range(1024)]
            ls_x = self.shared_data['shard'][0]
            ls_y = self.shared_data['shard'][1]
            ls_z = self.shared_data['shard'][2]

            # sampling_rate = 6500
            # # 对数据进行傅里叶变换
            # fft_result = fft(ls_x)
            # # 计算频率轴，根据采样率和数据长度
            # freq_axis_x = np.linspace(0, sampling_rate, len(ls_x))
            # # 可以用以下方式获取幅值谱
            # amplitude_spectrum_x = np.abs(fft_result)
            # # 可以用以下方式获取相位谱
            # # phase_spectrum = np.angle(fft_result)
            # fft_result = fft(ls_y)
            # freq_axis_y = np.linspace(0, sampling_rate, len(ls_y))
            # amplitude_spectrum_y = np.abs(fft_result)
            #
            # fft_result = fft(ls_z)
            # freq_axis_z = np.linspace(0, sampling_rate, len(ls_z))
            # amplitude_spectrum_z = np.abs(fft_result)

            fs = 6500
            t = np.arange(1024) / fs
            x = np.sin(2 * np.pi * 1000 * t) + 0.5 * np.sin(2 * np.pi * 2000 * t)
            data = np.array(ls_x)
            # Compute the squared envelope
            analytic_signal = signal.hilbert(data)
            envelope = np.abs(analytic_signal)
            squared_envelope = envelope ** 2

            # Compute the Fourier transform magnitude
            fft_mag = np.abs(fft(squared_envelope))

            # Compute the frequency axis
            freqs = fftfreq(len(squared_envelope), 1 / fs)
            freqs_x = freqs[:len(freqs) // 2]
            fft_mag_x = fft_mag[:len(freqs) // 2]

            data = np.array(ls_y)
            analytic_signal = signal.hilbert(data)
            envelope = np.abs(analytic_signal)
            squared_envelope = envelope ** 2
            fft_mag = np.abs(fft(squared_envelope))
            freqs = fftfreq(len(squared_envelope), 1 / fs)
            freqs_y = freqs[:len(freqs) // 2]
            fft_mag_y = fft_mag[:len(freqs) // 2]

            data = np.array(ls_z)
            analytic_signal = signal.hilbert(data)
            envelope = np.abs(analytic_signal)
            squared_envelope = envelope ** 2
            fft_mag = np.abs(fft(squared_envelope))
            freqs = fftfreq(len(squared_envelope), 1 / fs)
            freqs_z = freqs[:len(freqs) // 2]
            fft_mag_z = fft_mag[:len(freqs) // 2]

            for item in self.plot_9.items():
                if isinstance(item, pg.TextItem):
                    self.plot_9.removeItem(item)
            self.plot_9.clearPlots()

            for item in self.plot_10.items():
                if isinstance(item, pg.TextItem):
                    self.plot_10.removeItem(item)
            self.plot_10.clearPlots()

            for item in self.plot_11.items():
                if isinstance(item, pg.TextItem):
                    self.plot_11.removeItem(item)
            self.plot_11.clearPlots()

            for item in self.plot_12.items():
                if isinstance(item, pg.TextItem):
                    self.plot_12.removeItem(item)
            self.plot_12.clearPlots()

            for item in self.plot_13.items():
                if isinstance(item, pg.TextItem):
                    self.plot_13.removeItem(item)
            self.plot_13.clearPlots()

            for item in self.plot_14.items():
                if isinstance(item, pg.TextItem):
                    self.plot_14.removeItem(item)
            self.plot_14.clearPlots()

            # 绘制时域图
            self.plot_9.plot(lst, ls_x, pen=pg.mkPen(pg.intColor(0), width=2),
                             symbol='o', symbolSize=2)
            self.plot_9.autoRange()
            self.plot_10.plot(lst, ls_y, pen=pg.mkPen(pg.intColor(0), width=2),
                             symbol='o', symbolSize=2)
            self.plot_10.autoRange()
            self.plot_11.plot(lst, ls_z, pen=pg.mkPen(pg.intColor(0), width=2),
                             symbol='o', symbolSize=2)
            self.plot_11.autoRange()

            # # 绘制频谱图，x 轴为频率，y 轴为振幅
            # self.plot_12.plot(freq_axis_x, amplitude_spectrum_x, pen=pg.mkPen(pg.intColor(0), width=2),
            #                  symbol='o', symbolSize=2)
            # self.plot_12.autoRange()
            # self.plot_13.plot(freq_axis_y, amplitude_spectrum_y, pen=pg.mkPen(pg.intColor(0), width=2),
            #                   symbol='o', symbolSize=2)
            # self.plot_13.autoRange()
            # self.plot_14.plot(freq_axis_z, amplitude_spectrum_z, pen=pg.mkPen(pg.intColor(0), width=2),
            #                   symbol='o', symbolSize=2)
            # self.plot_14.autoRange()

            #平方包络的傅立叶变换幅度
            self.plot_12.plot(freqs_x, fft_mag_x, pen=pg.mkPen(pg.intColor(0), width=2),
                              symbol='o', symbolSize=2)
            self.plot_12.autoRange()
            self.plot_13.plot(freqs_y, fft_mag_y, pen=pg.mkPen(pg.intColor(0), width=2),
                              symbol='o', symbolSize=2)
            self.plot_13.autoRange()
            self.plot_14.plot(freqs_z, fft_mag_z, pen=pg.mkPen(pg.intColor(0), width=2),
                              symbol='o', symbolSize=2)
            self.plot_14.autoRange()

    def showFileDialog(self):
        # 打开文件选择对话框
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_name, _ = file_dialog.getOpenFileName(self, 'Select File')

        # 如果有选择文件，则打印文件路径
        if file_name:
            self.plotdata(file_name)

    def plotdata(self, file_name):
        mat_contents = sio.loadmat(file_name)
        for i in mat_contents.keys():
            if 'time' in i:
                data = mat_contents[i]
                break
        data = data.flatten().tolist()
        fft_data = np.fft.fft(data)
        freq = np.fft.fftfreq(len(data), d=1 / 12000)  # 采样频率为12000Hz

        for item in self.plot_7.items():
            if isinstance(item, pg.TextItem):
                self.plot_7.removeItem(item)
        self.plot_7.plot(data, pen=pg.mkPen(pg.intColor(0), width=2))
        self.plot_7.autoRange()
        for item in self.plot_8.items():
            if isinstance(item, pg.TextItem):
                self.plot_8.removeItem(item)
        self.plot_8.plot(freq[:int(len(freq) / 2)], np.abs(fft_data)[:int(len(fft_data) / 2)],
                         pen=pg.mkPen(pg.intColor(0), width=2))
        self.plot_8.autoRange()


def show(shared_data):
    app = QApplication(sys.argv)
    # 实例化页面并展示
    demo = DemoMain(shared_data)
    demo.show()
    sys.exit(app.exec_())


def getdata(shared_data):
    while True:
        if shared_data['flag'][0] == 0:
            data = RS485.communcation(1, 0, 22)
            shared_data['shard'] = data
            time.sleep(0.2)

        elif shared_data['flag'][0] == 1:
            data = RS485.communcation(1, 23, 120)
            shared_data['shard'] = data
            time.sleep(0.3)

        elif shared_data['flag'][0] == 2:
            data = RS485.communcation_1024()
            shared_data['shard'] = data
            time.sleep(0.3)

if __name__ == '__main__':
    manager = Manager()
    ls = []
    ls_2 = [0]
    shared_data = manager.dict({'shard': ls, 'flag': ls_2})
    p1 = Process(target=show, args=(shared_data,))
    p2 = Process(target=getdata, args=(shared_data,))
    p1.start()
    p2.start()
    p1.join()
    p2.terminate()
