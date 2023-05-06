import RS485
from multiprocessing import Process, Manager
import time
from mainwindow import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import QTimer
import datetime
import sql_select
from scipy import signal
import scipy.io as sio
from scipy.fft import fft, fftfreq
import numpy as np
import matlab.engine
import matlab
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class DemoMain(QMainWindow, Ui_MainWindow):
    def __init__(self, shared_data):
        # 初始化父类
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.shared_data = shared_data
        self.flag = 0
        self.stackedWidget.setMaximumHeight(900)
        self.showMaximized()
        self.init()

        # self.showMaximized()
        # self.comboBox.currentIndexChanged.connect(self.updateplot)
        # self.comboBox_2.currentIndexChanged.connect(self.updateplot_2)
        # self.comboBox_3.currentIndexChanged.connect(self.updateplot_3)

        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.comboBox.activated.connect(self.stackedChanged)
        self.comboBox_6.activated.connect(self.stackedChanged_6)
        self.comboBox_7.activated.connect(self.stackedChanged_7)
        self.pushButton_2.clicked.connect(self.analysis)
        self.pushButton_3.clicked.connect(self.calculate)
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

        self.tableWidget_2.setRowCount(21)
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
        item = QtWidgets.QTableWidgetItem('内圈特征频率')
        self.tableWidget_2.setItem(20, 0, item)
        item = QtWidgets.QTableWidgetItem('外圈特征频率')
        self.tableWidget_2.setItem(20, 2, item)
        item = QtWidgets.QTableWidgetItem('保持架特征频率')
        self.tableWidget_2.setItem(20, 4, item)

        self.tableWidget_2.verticalHeader().setVisible(False)
        self.tableWidget_2.horizontalHeader().setVisible(False)  # 行列序号取消
        self.tableWidget_2.resizeColumnsToContents()  # 根据内容调整列宽
        # self.tableWidget.resizeRowsToContents()#根据内容调整行高
        self.tableWidget_2.setFixedHeight(800)
        # self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.horizontalHeader().setMinimumSectionSize(100)

        self.tableWidget_3.setRowCount(2)
        self.tableWidget_3.setColumnCount(12)

        item = QtWidgets.QTableWidgetItem('滚珠个数')
        self.tableWidget_3.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem('9')
        self.tableWidget_3.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem('滚珠直径')
        self.tableWidget_3.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem('0.794')
        self.tableWidget_3.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem('轴承节径')
        self.tableWidget_3.setItem(0, 4, item)
        item = QtWidgets.QTableWidgetItem('3.904')
        self.tableWidget_3.setItem(0, 5, item)
        item = QtWidgets.QTableWidgetItem('接触角')
        self.tableWidget_3.setItem(0, 6, item)
        item = QtWidgets.QTableWidgetItem('0')
        self.tableWidget_3.setItem(0, 7, item)
        item = QtWidgets.QTableWidgetItem('转速')
        self.tableWidget_3.setItem(0, 8, item)
        item = QtWidgets.QTableWidgetItem('1615')
        self.tableWidget_3.setItem(0, 9, item)
        item = QtWidgets.QTableWidgetItem('内圈旋转频率')
        self.tableWidget_3.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem('内外圈相对旋转频率')
        self.tableWidget_3.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem('滚动体通过内圈一点的频率')
        self.tableWidget_3.setItem(1, 4, item)
        item = QtWidgets.QTableWidgetItem('滚动体通过外圈一点的频率')
        self.tableWidget_3.setItem(1, 6, item)
        item = QtWidgets.QTableWidgetItem('滚动体的公转频率')
        self.tableWidget_3.setItem(1, 8, item)
        item = QtWidgets.QTableWidgetItem('保持架旋转频率')
        self.tableWidget_3.setItem(1, 10, item)
        item = QtWidgets.QTableWidgetItem('26.9')
        self.tableWidget_3.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem('26.9')
        self.tableWidget_3.setItem(1, 3, item)
        item = QtWidgets.QTableWidgetItem('145.8')
        self.tableWidget_3.setItem(1, 5, item)
        item = QtWidgets.QTableWidgetItem('96.5')
        self.tableWidget_3.setItem(1, 7, item)
        item = QtWidgets.QTableWidgetItem('10.7')
        self.tableWidget_3.setItem(1, 9, item)
        item = QtWidgets.QTableWidgetItem('10.7')
        self.tableWidget_3.setItem(1, 11, item)
        self.pushButton_3 = QtWidgets.QPushButton()
        self.pushButton_3.setText('计算特征值')
        self.tableWidget_3.setSpan(0, 10, 1, 2)  # 第2行3~6列合并为1个单元格
        self.tableWidget_3.setIndexWidget(self.tableWidget_3.model().index(0, 10), self.pushButton_3)  # 第0行，第0列的单元格添加按钮

        self.tableWidget_3.verticalHeader().setVisible(False)
        self.tableWidget_3.horizontalHeader().setVisible(False)  # 行列序号取消
        self.tableWidget_3.resizeColumnsToContents()  # 根据内容调整列宽
        # self.tableWidget.resizeRowsToContents()#根据内容调整行高
        self.tableWidget_3.setFixedHeight(100)
        self.tableWidget_3.horizontalHeader().setMinimumSectionSize(100)

        self.tableWidget_4.setRowCount(2)
        self.tableWidget_4.setColumnCount(14)

        item = QtWidgets.QTableWidgetItem('滚珠个数')
        self.tableWidget_4.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem('滚珠直径')
        self.tableWidget_4.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem('轴承节径')
        self.tableWidget_4.setItem(0, 4, item)
        item = QtWidgets.QTableWidgetItem('接触角')
        self.tableWidget_4.setItem(0, 6, item)
        item = QtWidgets.QTableWidgetItem('转速')
        self.tableWidget_4.setItem(0, 8, item)
        item = QtWidgets.QTableWidgetItem('8')
        self.tableWidget_4.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem('0.235')
        self.tableWidget_4.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem('1.245')
        self.tableWidget_4.setItem(0, 5, item)
        item = QtWidgets.QTableWidgetItem('0')
        self.tableWidget_4.setItem(0, 7, item)
        item = QtWidgets.QTableWidgetItem('1500')
        self.tableWidget_4.setItem(0, 9, item)
        item = QtWidgets.QTableWidgetItem('内圈旋转频率')
        self.tableWidget_4.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem('内外圈相对旋转频率')
        self.tableWidget_4.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem('滚动体通过内圈一点的频率')
        self.tableWidget_4.setItem(1, 4, item)
        item = QtWidgets.QTableWidgetItem('滚动体通过外圈一点的频率')
        self.tableWidget_4.setItem(1, 6, item)
        item = QtWidgets.QTableWidgetItem('滚动体的公转频率')
        self.tableWidget_4.setItem(1, 8, item)
        item = QtWidgets.QTableWidgetItem('保持架旋转频率')
        self.tableWidget_4.setItem(1, 10, item)
        item = QtWidgets.QTableWidgetItem('25.0')
        self.tableWidget_4.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem('25.0')
        self.tableWidget_4.setItem(1, 3, item)
        item = QtWidgets.QTableWidgetItem('118.9')
        self.tableWidget_4.setItem(1, 5, item)
        item = QtWidgets.QTableWidgetItem('81.1')
        self.tableWidget_4.setItem(1, 7, item)
        item = QtWidgets.QTableWidgetItem('10.1')
        self.tableWidget_4.setItem(1, 9, item)
        item = QtWidgets.QTableWidgetItem('10.1')
        self.tableWidget_4.setItem(1, 11, item)
        item = QtWidgets.QTableWidgetItem('特征频率分析结果')
        self.tableWidget_4.setItem(1, 12, item)

        self.tableWidget_4.verticalHeader().setVisible(False)
        self.tableWidget_4.horizontalHeader().setVisible(False)  # 行列序号取消
        self.tableWidget_4.resizeColumnsToContents()  # 根据内容调整列宽
        # self.tableWidget.resizeRowsToContents()#根据内容调整行高
        self.tableWidget_4.setFixedHeight(100)
        self.tableWidget_4.horizontalHeader().setMinimumSectionSize(100)

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

        self.plot_4 = pg.PlotWidget()
        self.plot_5 = pg.PlotWidget()
        #self.plot_6 = pg.PlotWidget()

        self.plot_7 = pg.PlotWidget()
        self.plot_8 = pg.PlotWidget()

        self.plot_9 = pg.PlotWidget()
        self.plot_10 = pg.PlotWidget()
        self.plot_11 = pg.PlotWidget()
        self.plot_12 = pg.PlotWidget()
        self.plot_13 = pg.PlotWidget()
        self.plot_14 = pg.PlotWidget()
        self.plot_15 = pg.PlotWidget()
        self.plot_16 = pg.PlotWidget()
        self.plot_17 = pg.PlotWidget()
        self.plot_18 = pg.PlotWidget()
        self.plot_19 = pg.PlotWidget()
        self.plot_21 = pg.PlotWidget()
        self.plot_22 = pg.PlotWidget()
        self.plot_23 = pg.PlotWidget()


        self.plot.setBackground('w')
        self.plot_2.setBackground('w')
        self.plot_3.setBackground('w')
        self.plot_4.setBackground('w')
        self.plot_5.setBackground('w')
        #self.plot_6.setBackground('w')
        self.plot_7.setBackground('w')
        self.plot_8.setBackground('w')
        self.plot_9.setBackground('w')
        self.plot_10.setBackground('w')
        self.plot_11.setBackground('w')
        self.plot_12.setBackground('w')
        self.plot_13.setBackground('w')
        self.plot_14.setBackground('w')
        self.plot_15.setBackground('w')
        self.plot_16.setBackground('w')
        self.plot_17.setBackground('w')
        self.plot_18.setBackground('w')
        self.plot_19.setBackground('w')
        self.plot_21.setBackground('w')
        self.plot_22.setBackground('w')
        self.plot_23.setBackground('w')

        self.widget_4.setLayout(QtWidgets.QVBoxLayout())
        self.widget_4.layout().addWidget(self.plot_4)
        self.widget_5.setLayout(QtWidgets.QVBoxLayout())
        self.widget_5.layout().addWidget(self.plot_5)
        self.widget_6.setLayout(QtWidgets.QVBoxLayout())
        #self.widget_6.layout().addWidget(self.plot_6)
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
        self.widget_15.setLayout(QtWidgets.QVBoxLayout())
        self.widget_15.layout().addWidget(self.plot_15)

        self.widget_16.setLayout(QtWidgets.QVBoxLayout())
        self.widget_16.layout().addWidget(self.plot_16)
        self.widget_17.setLayout(QtWidgets.QVBoxLayout())
        self.widget_17.layout().addWidget(self.plot_17)
        self.widget_18.setLayout(QtWidgets.QVBoxLayout())
        self.widget_18.layout().addWidget(self.plot_18)
        self.widget_19.setLayout(QtWidgets.QVBoxLayout())
        self.widget_19.layout().addWidget(self.plot_19)
        self.widget_20.setLayout(QtWidgets.QVBoxLayout())

        self.widget_21.setLayout(QtWidgets.QVBoxLayout())
        self.widget_21.layout().addWidget(self.plot_21)
        self.widget_22.setLayout(QtWidgets.QVBoxLayout())
        self.widget_22.layout().addWidget(self.plot_22)
        self.widget_23.setLayout(QtWidgets.QVBoxLayout())
        self.widget_23.layout().addWidget(self.plot_23)

        # self.plot.plot(self.x, self.y, pen=pg.mkPen('b', width=2))
        # 设置 x 轴范围为 0-3000毫秒，y 轴范围为 0-10
        self.plot.setRange(xRange=[0, 3000], yRange=[0, 50])
        # 设置时间轴单位为毫秒
        self.plot.setLabel('bottom', 'Time', units='ms')
        # self.plot.setLabel('top', 'Top Label')
        # self.plot.getAxis('top').setStyle(tickLength=0, showValues=False)
        # self.plot.getAxis('top').setPen(pg.mkPen(None))

        self.plot_2.setRange(xRange=[0, 3000], yRange=[0, 50])
        # 设置时间轴单位为毫
        self.plot_2.setLabel('bottom', 'Time', units='ms')
        self.plot_3.setRange(xRange=[0, 3000], yRange=[0, 50])
        # 设置时间轴单位为毫秒
        self.plot_3.setLabel('bottom', 'Time', units='ms')

        self.plot_9.setLabel('top', '实时加速度波形')
        self.plot_9.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_9.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_10.setLabel('top', '实时功率谱图形')
        self.plot_10.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_10.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_11.setLabel('top', '实时加速度包络图形')
        self.plot_11.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_11.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_12.setLabel('top', '实时包络谱分析图形')
        self.plot_12.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_12.getAxis('top').setPen(pg.mkPen('k'))

        self.plot_4.setLabel('top', '实时加速度波形')
        self.plot_4.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_4.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_5.setLabel('top', '实时加速度包络图形')
        self.plot_5.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_5.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_13.setLabel('top', '谱峭度图形')
        self.plot_13.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_13.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_14.setLabel('top', '滤波后的包络图形')
        self.plot_14.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_14.getAxis('top').setPen(pg.mkPen('k'))

        self.plot_15.setLabel('top', '滤波后的包络谱分析图形')
        self.plot_15.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_15.getAxis('top').setPen(pg.mkPen('k'))

        self.plot_16.setLabel('top', '实时加速度波形')
        self.plot_16.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_16.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_18.setLabel('top', '实时功率谱图形')
        self.plot_18.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_18.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_17.setLabel('top', '实时加速度包络图形')
        self.plot_17.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_17.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_19.setLabel('top', '实时包络谱分析图形')
        self.plot_19.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_19.getAxis('top').setPen(pg.mkPen('k'))

        self.plot_7.setLabel('top', '实时加速度波形')
        self.plot_7.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_7.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_8.setLabel('top', '实时加速度包络图形')
        self.plot_8.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_8.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_21.setLabel('top', '谱峭度图形')
        self.plot_21.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_21.getAxis('top').setPen(pg.mkPen('k'))
        self.plot_22.setLabel('top', '滤波后的包络图形')
        self.plot_22.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_22.getAxis('top').setPen(pg.mkPen('k'))

        self.plot_23.setLabel('top', '滤波后的包络谱分析图形')
        self.plot_23.getAxis('top').setStyle(tickLength=0, showValues=False)
        self.plot_23.getAxis('top').setPen(pg.mkPen('k'))


        self.plot.getAxis('bottom').setPen(pg.mkPen('k'))
        self.plot_2.getAxis('bottom').setPen(pg.mkPen('k'))
        self.plot_3.getAxis('bottom').setPen(pg.mkPen('k'))
        # self.plot.getAxis('left').setPen(pg.mkPen('k'))
        # self.plot.getAxis('bottom').setPen(pg.mkPen(color='r'))
        # self.plot.getAxis('left').setPen(pg.mkPen(color='g'))

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

        self.comboBox_5.addItem('x轴')
        self.comboBox_5.addItem('y轴')
        self.comboBox_5.addItem('z轴')
        self.comboBox_6.addItem('内圈故障分析')
        self.comboBox_6.addItem('外圈故障分析')

        self.comboBox_7.addItem('内圈故障分析')
        self.comboBox_7.addItem('外圈故障分析')

        self.pushButton.setText('Select File')
        self.pushButton.clicked.connect(self.showFileDialog)

    def stackedChanged_6(self, index):
        if index == 0:
            self.stackedWidget_2.setCurrentIndex(0)
        elif index == 1:
            self.stackedWidget_2.setCurrentIndex(1)

    def stackedChanged_7(self, index):
        if index == 0:
            self.stackedWidget_3.setCurrentIndex(0)
        elif index == 1:
            self.stackedWidget_3.setCurrentIndex(1)

    def stackedChanged(self, index):
        if index == 0:
            # self.timer2.stop()
            self.timer1.start()
            self.timer.start()
            self.stackedWidget.setCurrentIndex(0)
            temp = self.shared_data['flag']
            temp[0] = 0
            self.shared_data['flag'] = temp
        elif index == 1:
            self.timer.start()
            # self.timer2.stop()
            self.timer1.stop()
            self.stackedWidget.setCurrentIndex(1)
            temp = self.shared_data['flag']
            temp[0] = 1
            self.shared_data['flag'] = temp
        elif index == 2:
            self.timer.stop()
            self.timer1.stop()
            self.stackedWidget.setCurrentIndex(2)
            # self.flag = self.flag + 1
            temp = self.shared_data['flag']
            temp[0] = 2
            # temp[1] = self.flag
            self.shared_data['flag'] = temp
            # self.timer2.start()

    def tabChanged(self, index):
        if index == 0:
            if self.stackedWidget.currentIndex() == 0:
                self.timer.start()
                self.timer1.start()
                temp = self.shared_data['flag']
                temp[0] = 0
                self.shared_data['flag'] = temp
            if self.stackedWidget.currentIndex() == 1:
                self.timer.start()
                temp = self.shared_data['flag']
                temp[0] = 1
                self.shared_data['flag'] = temp
            if self.stackedWidget.currentIndex() == 2:
                temp = self.shared_data['flag']
                temp[0] = 2
                self.shared_data['flag'] = temp

        elif index == 1:
            self.timer.stop()
            self.timer1.stop()
            temp = self.shared_data['flag']
            temp[0] = -1
            self.shared_data['flag'] = temp

    def updateData(self):
        # if len(self.shared_data['shard'])>=20:
        if self.stackedWidget.currentIndex() == 0:
            if len(self.shared_data['shard']) == 22:
                row = 0
                col = 1
                for i in range(22):
                    if i == 3:
                        pass
                    else:
                        item = QtWidgets.QTableWidgetItem(str(self.shared_data['shard'][i]))
                        self.tableWidget.setItem(row, col, item)
                        # print(row, col, item)
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
            # print(1)
            if len(self.shared_data['shard']) == 120:
                row = 0
                col = 1
                for i in range(len(self.shared_data['shard'])):
                    item = QtWidgets.QTableWidgetItem(str(self.shared_data['shard'][i]))
                    self.tableWidget_2.setItem(row, col, item)
                    # print(row, col, item)
                    if row < 19:
                        row += 1
                    else:
                        row = 0
                        col += 2

                fic = str(round(4.5 * (1 + 0.794 / 3.904) * 1615 / 60, 1))  # = 内圈特征频率
                foc = str(round(4.5 * (1 - 0.794 / 3.904) * 1615 / 60, 1))  # = 外圈特征频率
                fc = str(round(0.5 * (1 - 0.794 / 3.904) * 1615 / 60, 1))  # = 保持架特征频率
                item = QtWidgets.QTableWidgetItem(fic)
                self.tableWidget_2.setItem(20, 1, item)
                item = QtWidgets.QTableWidgetItem(foc)
                self.tableWidget_2.setItem(20, 3, item)
                item = QtWidgets.QTableWidgetItem(fc)
                self.tableWidget_2.setItem(20, 5, item)

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

            self.plot.plot(xtime, xdata, pen=pg.mkPen(pg.intColor(6), width=2),
                           symbol='o', symbolSize=2)
            self.plot.autoRange()
            self.plot.setRange(xRange=[0, 30000])
            self.plot_2.plot(ytime, ydata, pen=pg.mkPen(pg.intColor(6), width=2),
                             symbol='o', symbolSize=2)
            self.plot_2.autoRange()
            self.plot_2.setRange(xRange=[0, 30000])
            self.plot_3.plot(ztime, zdata, pen=pg.mkPen(pg.intColor(6), width=2),
                             symbol='o', symbolSize=2)
            self.plot_3.autoRange()
            self.plot_3.setRange(xRange=[0, 30000])

    def update_plotdata_1024(self):
        # if len(self.shared_data['shard']) == 3:
        #     lst = [i for i in range(1024)]
        #     ls_x = self.shared_data['shard'][0]
        #     ls_y = self.shared_data['shard'][1]
        #     ls_z = self.shared_data['shard'][2]
        #
        #     # sampling_rate = 6500
        #     # # 对数据进行傅里叶变换
        #     # fft_result = fft(ls_x)
        #     # # 计算频率轴，根据采样率和数据长度
        #     # freq_axis_x = np.linspace(0, sampling_rate, len(ls_x))
        #     # # 可以用以下方式获取幅值谱
        #     # amplitude_spectrum_x = np.abs(fft_result)
        #     # # 可以用以下方式获取相位谱
        #     # # phase_spectrum = np.angle(fft_result)
        #     # fft_result = fft(ls_y)
        #     # freq_axis_y = np.linspace(0, sampling_rate, len(ls_y))
        #     # amplitude_spectrum_y = np.abs(fft_result)
        #     #
        #     # fft_result = fft(ls_z)
        #     # freq_axis_z = np.linspace(0, sampling_rate, len(ls_z))
        #     # amplitude_spectrum_z = np.abs(fft_result)
        #
        #     fs = 6500
        #     t = np.arange(1024) / fs
        #     x = np.sin(2 * np.pi * 1000 * t) + 0.5 * np.sin(2 * np.pi * 2000 * t)
        #     data = np.array(ls_x)
        #     # Compute the squared envelope
        #     analytic_signal = signal.hilbert(data)
        #     envelope = np.abs(analytic_signal)
        #     squared_envelope = envelope ** 2
        #
        #     # Compute the Fourier transform magnitude
        #     fft_mag = np.abs(fft(squared_envelope))
        #
        #     # Compute the frequency axis
        #     freqs = fftfreq(len(squared_envelope), 1 / fs)
        #     freqs_x = freqs[:len(freqs) // 2]
        #     fft_mag_x = fft_mag[:len(freqs) // 2]
        #
        #     data = np.array(ls_y)
        #     analytic_signal = signal.hilbert(data)
        #     envelope = np.abs(analytic_signal)
        #     squared_envelope = envelope ** 2
        #     fft_mag = np.abs(fft(squared_envelope))
        #     freqs = fftfreq(len(squared_envelope), 1 / fs)
        #     freqs_y = freqs[:len(freqs) // 2]
        #     fft_mag_y = fft_mag[:len(freqs) // 2]
        #
        #     data = np.array(ls_z)
        #     analytic_signal = signal.hilbert(data)
        #     envelope = np.abs(analytic_signal)
        #     squared_envelope = envelope ** 2
        #     fft_mag = np.abs(fft(squared_envelope))
        #     freqs = fftfreq(len(squared_envelope), 1 / fs)
        #     freqs_z = freqs[:len(freqs) // 2]
        #     fft_mag_z = fft_mag[:len(freqs) // 2]
        if len(self.shared_data['shard']) == 10240:
            # print(self.shared_data['shard'])
            lst = [i for i in range(10240)]
            gsdi = matlab.double(self.shared_data['shard'])
            srdi = 6500.0
            # ---------------外圈加速度和采样率获取------------------------------
            # gso = scio.loadmat(path_mat)['gso']
            # sro = scio.loadmat(path_mat)['sro']
            # gsdo = matlab.double(gso.tolist())
            # srdo = matlab.double(sro.tolist())

            eng = matlab.engine.start_matlab()  # 可以调用matlab的内置函数。
            # ------------内圈特征频率分析-----------------------------------------
            # print('kurtosis=',eng.kurtosis(gsdi))
            [pInner, fpInner] = eng.pspectrum(gsdi, srdi, nargout=2)  # 采集信号的直接功率谱图，x轴频率，y轴功率谱大小2222222222222
            [pEnvInner, fEnvInner, xEnvInner, tEnvInner] = eng.envspectrum(gsdi, srdi,
                                                                           nargout=4)  # 包络谱分析； # fEnvInner,频率；pEnvInner,包络谱峰值； xEnvInner,包络大小，tEnvInner，时间
            # eng.plot(tEnvInner[1:3000], xEnvInner[1:3000])  # title: 时间VS包络；[]中的范围可以根据大小修改
            # eng.plot(fEnvInner[1:3000], pEnvInner[1:3000])  # title :如果是内圈故障的话，直接分析包络，得到内圈特征频率，频率vs包络谱
            fpInner = [item for sublist in fpInner for item in sublist]
            pInner = [item for sublist in pInner for item in sublist]
            pEnvInner = [item for sublist in pEnvInner for item in sublist]
            fEnvInner = [item for sublist in fEnvInner for item in sublist]
            xEnvInner = [item for sublist in xEnvInner for item in sublist]
            tEnvInner = [item for sublist in tEnvInner for item in sublist]
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

            # for item in self.plot_13.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_13.removeItem(item)
            # self.plot_13.clearPlots()
            #
            # for item in self.plot_14.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_14.removeItem(item)
            # self.plot_14.clearPlots()

            # 绘制时域图
            self.plot_9.plot(lst, self.shared_data['shard'],
                             pen=pg.mkPen(pg.intColor(6), width=1))  # ,symbol='o', symbolSize=2
            self.plot_9.autoRange()

            self.plot_10.plot(fpInner, pInner, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_10.autoRange()

            self.plot_11.plot(tEnvInner, xEnvInner, pen=pg.mkPen(pg.intColor(6), width=1))
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

            # 平方包络的傅立叶变换幅度
            self.plot_12.plot(fEnvInner[0:1600], pEnvInner[0:1600], pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_12.autoRange()
            # self.plot_13.plot(freqs_y, fft_mag_y, pen=pg.mkPen(pg.intColor(6), width=2),
            #                   symbol='o', symbolSize=2)
            # self.plot_13.autoRange()
            # self.plot_14.plot(freqs_z, fft_mag_z, pen=pg.mkPen(pg.intColor(6), width=2),
            #                   symbol='o', symbolSize=2)
            # self.plot_14.autoRange()

            gsdo = matlab.double(self.shared_data['shard'])
            srdo = 6500.0

            #eng = matlab.engine.start_matlab()  # 可以调用matlab的内置函数。
            #level = 9
            [pEnvOuter, fEnvOuter, xEnvOuter, tEnvOuter] = eng.envspectrum(gsdo, srdo,
                                                                           nargout=4)  # 包络谱分析； # fEnvInner,频率；pEnvInner,包络谱峰值； xEnvInner,包络大小，tEnvInner，时间
            [kgram, f, w, fc, wc, BW] = eng.kurtogram(gsdo, srdo, 7.0,
                                                      nargout=6)  # kgram 为 len(w)*len(f)的矩阵,横坐标表示频率，纵坐标表示窗长度，取值表示峭度。需要二维作图

            ff = eng.linspace(0.0, srdo/2, 384)
            max_w = float(np.max(w))
            min_w = float(np.min(w))
            ww = eng.linspace(max_w, min_w, 14)
            #ww = eng.linspace(max_w, min_w, 18)
            #ww = eng.linspace(max(w), min(w), 18)
            self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
            X, Y = np.meshgrid(ff, ww)
            #self.ax.contourf(X, Y, kgram, cmap=plt.cm.jet)
            CS = self.ax.contourf(X, Y, kgram, cmap=plt.cm.jet, extend='both')
           # 添加图例
            self.fig.colorbar(CS)
            #self.ax.contourf(ff, ww, kgram, cmap=plt.cm.jet)
           # 创建 FigureCanvas 和 NavigationToolbar
            self.canvas = FigureCanvas(self.fig)
            self.toolbar = NavigationToolbar(self.canvas, self)
            while self.widget_6.layout().count():
                child = self.widget_6.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                else:
                    del child
            self.widget_6.layout().addWidget(self.canvas)
            self.widget_6.layout().addWidget(self.toolbar)
            [sk, fout] = eng.pkurtosis(gsdo, srdo, nargout=2)  # 谱峭度，sk为峭度值，fout为频率
            # print(fc)
            # print(BW)
            # print(wc)
            # print(kgram)
            if (fc - BW / 2)<=0:
                if (fc + BW / 2)>=3250:
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 4,
                                         'CutoffFrequency2', 3245, 'SampleRate', srdo, nargout=1)
                else:
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 4,
                                         'CutoffFrequency2', fc + BW / 2, 'SampleRate', srdo, nargout=1)
            else:
                if (fc + BW / 2) >= 3250:
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 2,
                                     'CutoffFrequency2', 3245, 'SampleRate', srdo, nargout=1)
                else:
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 2,
                                         'CutoffFrequency2', fc + BW / 2, 'SampleRate', srdo, nargout=1)

            xOuterBpf = eng.filter(bpf, gsdo, nargout=1)
            tmp = [[fc - BW / 2], [fc + BW / 2]]
            [pEnvOuterBpf, fEnvOuterBpf, xEnvOuterBpf, tEnvBpfOuter] = eng.envspectrum(gsdo, srdo, 'FilterOrder',
                                                                                       200.0, 'Band',
                                                                                       matlab.double(tmp),
                                                                                       nargout=4)

            tEnvOuter = [item for sublist in tEnvOuter for item in sublist]
            xEnvOuter = [item for sublist in xEnvOuter for item in sublist]
            # fEnvOuter = [item for sublist in fEnvOuter for item in sublist]
            # pEnvOuter = [item for sublist in pEnvOuter for item in sublist]
            sk = [item for sublist in sk for item in sublist]
            fout = [item for sublist in fout for item in sublist]
            xEnvOuterBpf = [item for sublist in xEnvOuterBpf for item in sublist]
            tEnvBpfOuter = [item for sublist in tEnvBpfOuter for item in sublist]
            pEnvOuterBpf = [item for sublist in pEnvOuterBpf for item in sublist]
            fEnvOuterBpf = [item for sublist in fEnvOuterBpf for item in sublist]

            for item in self.plot_4.items():
                if isinstance(item, pg.TextItem):
                    self.plot_4.removeItem(item)
            self.plot_4.clearPlots()

            for item in self.plot_5.items():
                if isinstance(item, pg.TextItem):
                    self.plot_5.removeItem(item)
            self.plot_5.clearPlots()

            # for item in self.plot_6.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_6.removeItem(item)
            # self.plot_6.clearPlots()

            for item in self.plot_13.items():
                if isinstance(item, pg.TextItem):
                    self.plot_13.removeItem(item)
            self.plot_13.clearPlots()

            for item in self.plot_14.items():
                if isinstance(item, pg.TextItem):
                    self.plot_14.removeItem(item)
            self.plot_14.clearPlots()

            for item in self.plot_15.items():
                if isinstance(item, pg.TextItem):
                    self.plot_15.removeItem(item)
            self.plot_15.clearPlots()

            self.plot_4.plot(lst, self.shared_data['shard'],
                             pen=pg.mkPen(pg.intColor(6), width=1))  # ,symbol='o', symbolSize=2
            self.plot_4.autoRange()

            self.plot_5.plot(tEnvOuter, xEnvOuter,
                             pen=pg.mkPen(pg.intColor(6), width=1))  # ,symbol='o', symbolSize=2
            self.plot_5.autoRange()

            self.plot_13.plot(fout, sk, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_13.autoRange()

            self.plot_14.plot(tEnvBpfOuter, xEnvOuterBpf, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_14.autoRange()

            self.plot_15.plot(fEnvOuterBpf[0:300], pEnvOuterBpf[0:300], pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_15.autoRange()

            self.timer2.stop()

    def showFileDialog(self):
        # 打开文件选择对话框
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_name, _ = file_dialog.getOpenFileName(self, 'Select File')

        # 如果有选择文件，则打印文件路径
        if file_name:
            print(file_name)
            self.plotdata(file_name)

    def analysis(self):
        self.flag = self.flag + 1
        temp = self.shared_data['flag']
        # temp[0] = 2
        temp[1] = self.flag
        if self.comboBox_5.currentText() == 'x轴':
            temp[2] = 5
        if self.comboBox_5.currentText() == 'y轴':
            temp[2] = 6
        if self.comboBox_5.currentText() == 'z轴':
            temp[2] = 7
        self.shared_data['flag'] = temp
        print(self.shared_data['flag'])
        self.timer2.start()

    def calculate(self):
        z = float(self.tableWidget_3.item(0, 1).text())
        d = float(self.tableWidget_3.item(0, 3).text())
        D = float(self.tableWidget_3.item(0, 5).text())
        a = float(self.tableWidget_3.item(0, 7).text())
        fr = float(self.tableWidget_3.item(0, 9).text())

        cos = math.cos(a)  # cosa a为角度
        fre1 = fr / 60  # 旋转频率fre1 = n/60  [n为转速]
        frei = z / 2 * (1 + (d / D) * cos) * fre1  # 内圈旋转频率 = z/2(1+d/D)*fre1 [z为滚珠数=9，d为直径=0.794，D为节径=3.904]
        freo = z / 2 * (1 - (d / D) * cos) * fre1  # 外圈旋转频率 = z/2(1-d/D)*fre1
        fre2 = 0.5 * (1 - (d / D) * cos) * fre1  # 保持架旋转频率 = 0.5(1-d/D)*fre1

        fre1 = str(round(fre1, 1))
        frei = str(round(frei, 1))
        freo = str(round(freo, 1))
        fre2 = str(round(fre2, 1))

        item = QtWidgets.QTableWidgetItem(fre1)
        self.tableWidget_3.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem(fre1)
        self.tableWidget_3.setItem(1, 3, item)
        item = QtWidgets.QTableWidgetItem(frei)
        self.tableWidget_3.setItem(1, 5, item)
        item = QtWidgets.QTableWidgetItem(freo)
        self.tableWidget_3.setItem(1, 7, item)
        item = QtWidgets.QTableWidgetItem(fre2)
        self.tableWidget_3.setItem(1, 9, item)
        item = QtWidgets.QTableWidgetItem(fre2)
        self.tableWidget_3.setItem(1, 11, item)

    def plotdata(self, file_name):
        mat_contents = sio.loadmat(file_name)

        fs = mat_contents['sr'][0][0]
        data = mat_contents['gs'][0][0:50000]
        #print(data)
        # print(self.shared_data['shard'])
        lst = [i for i in range(len(data))]
        if self.comboBox_7.currentText()=='内圈故障分析':
            gsdi = matlab.double(data.tolist())
            srdi = float(fs)
            # print(gsdi)
            # print(srdi)
            # ---------------外圈加速度和采样率获取------------------------------
            # gso = scio.loadmat(path_mat)['gso']
            # sro = scio.loadmat(path_mat)['sro']
            # gsdo = matlab.double(gso.tolist())
            # srdo = matlab.double(sro.tolist())

            eng = matlab.engine.start_matlab()  # 可以调用matlab的内置函数。
            # ------------内圈特征频率分析-----------------------------------------
            # print('kurtosis=',eng.kurtosis(gsdi))
            [pInner, fpInner] = eng.pspectrum(gsdi, srdi, nargout=2)  # 采集信号的直接功率谱图，x轴频率，y轴功率谱大小2222222222222
            [pEnvInner, fEnvInner, xEnvInner, tEnvInner] = eng.envspectrum(gsdi, srdi,
                                                                           nargout=4)  # 包络谱分析； # fEnvInner,频率；pEnvInner,包络谱峰值； xEnvInner,包络大小，tEnvInner，时间
            #print(fpInner)
            # eng.plot(tEnvInner[1:3000], xEnvInner[1:3000])  # title: 时间VS包络；[]中的范围可以根据大小修改
            # eng.plot(fEnvInner[1:3000], pEnvInner[1:3000])  # title :如果是内圈故障的话，直接分析包络，得到内圈特征频率，频率vs包络谱
            fpInner = [item for sublist in fpInner for item in sublist]
            #print(1)
            pInner = [item for sublist in pInner for item in sublist]
            pEnvInner = [item for sublist in pEnvInner for item in sublist]
            fEnvInner = [item for sublist in fEnvInner for item in sublist]
            xEnvInner = [item for sublist in xEnvInner for item in sublist]
            tEnvInner = [item for sublist in tEnvInner for item in sublist]
            for item in self.plot_16.items():
                if isinstance(item, pg.TextItem):
                    self.plot_16.removeItem(item)
            self.plot_16.clearPlots()

            for item in self.plot_18.items():
                if isinstance(item, pg.TextItem):
                    self.plot_18.removeItem(item)
            self.plot_18.clearPlots()

            for item in self.plot_17.items():
                if isinstance(item, pg.TextItem):
                    self.plot_17.removeItem(item)
            self.plot_17.clearPlots()

            for item in self.plot_19.items():
                if isinstance(item, pg.TextItem):
                    self.plot_19.removeItem(item)
            self.plot_19.clearPlots()

            # for item in self.plot_13.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_13.removeItem(item)
            # self.plot_13.clearPlots()
            #
            # for item in self.plot_14.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_14.removeItem(item)
            # self.plot_14.clearPlots()

            # 绘制时域图
            self.plot_16.plot(lst,data.tolist(),
                             pen=pg.mkPen(pg.intColor(6), width=1))  # ,symbol='o', symbolSize=2
            self.plot_16.autoRange()

            self.plot_18.plot(fpInner, pInner, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_18.autoRange()

            self.plot_17.plot(tEnvInner, xEnvInner, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_17.autoRange()

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

            # 平方包络的傅立叶变换幅度
            self.plot_19.plot(fEnvInner, pEnvInner, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_19.autoRange()
            # self.plot_13.plot(freqs_y, fft_mag_y, pen=pg.mkPen(pg.intColor(6), width=2),
            #                   symbol='o', symbolSize=2)
            # self.plot_13.autoRange()
            # self.plot_14.plot(freqs_z, fft_mag_z, pen=pg.mkPen(pg.intColor(6), width=2),
            #                   symbol='o', symbolSize=2)
            # self.plot_14.autoRange()
            max_index = pEnvInner.index(max(pEnvInner))
            item = QtWidgets.QTableWidgetItem(str(round(fEnvInner[max_index], 2)))
            item.setForeground(QtGui.QBrush(QtCore.Qt.red))  # 设置字体颜色为红色
            font = QtGui.QFont()
            font.setPointSize(12)  # 设置字体大小为12
            font.setBold(True)  # 设置字体加粗
            item.setFont(font)  # 设置字体
            self.tableWidget_4.setItem(1, 13, item)

        elif self.comboBox_7.currentText() == '外圈故障分析':
            gsdo = matlab.double(data.tolist())
            srdo = float(fs)

            eng = matlab.engine.start_matlab()  # 可以调用matlab的内置函数。
            # level = 9
            [pEnvOuter, fEnvOuter, xEnvOuter, tEnvOuter] = eng.envspectrum(gsdo, srdo,
                                                                           nargout=4)  # 包络谱分析； # fEnvInner,频率；pEnvInner,包络谱峰值； xEnvInner,包络大小，tEnvInner，时间
            [kgram, f, w, fc, wc, BW] = eng.kurtogram(gsdo, srdo, 7.0,
                                                      nargout=6)  # kgram 为 len(w)*len(f)的矩阵,横坐标表示频率，纵坐标表示窗长度，取值表示峭度。需要二维作图

            ff = eng.linspace(0.0, srdo / 2, 384)
            max_w = float(np.max(w))
            min_w = float(np.min(w))
            ww = eng.linspace(max_w, min_w, 14)
            # ww = eng.linspace(max_w, min_w, 18)
            # ww = eng.linspace(max(w), min(w), 18)
            self.fig_2, self.ax_2 = plt.subplots(figsize=(5, 4), dpi=100)
            X, Y = np.meshgrid(ff, ww)
            # self.ax_2.contourf(X, Y, kgram, cmap=plt.cm.jet)
            CS = self.ax_2.contourf(X, Y, kgram, cmap=plt.cm.jet, extend='both')
            # 添加图例
            self.fig_2.colorbar(CS)
            # self.ax_2.contourf(ff, ww, kgram, cmap=plt.cm.jet)
            # 创建 FigureCanvas 和 NavigationToolbar
            self.canvas_2 = FigureCanvas(self.fig_2)
            self.toolbar_2 = NavigationToolbar(self.canvas_2, self)
            # 查找子控件
            # canvas = self.widget_20.findChild(QtWidgets.QWidget, "canvas_2")
            # toolbar = self.widget_20.findChild(QtWidgets.QToolBar, "toolbar_2")
            #
            # # 如果存在则从布局中移除
            # if canvas:
            #     self.widget_20.layout().removeWidget(canvas)
            #     canvas.deleteLater()
            # if toolbar:
            #     self.widget_20.layout().removeWidget(toolbar)
            #     toolbar.deleteLater()
            while self.widget_20.layout().count():
                child = self.widget_20.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                else:
                    del child
            #self.widget_20.setLayout(QtWidgets.QVBoxLayout())
            self.widget_20.layout().addWidget(self.canvas_2)
            self.widget_20.layout().addWidget(self.toolbar_2)

            [sk, fout] = eng.pkurtosis(gsdo, srdo, nargout=2)  # 谱峭度，sk为峭度值，fout为频率
            # print(fc)
            # print(BW)
            # print(wc)
            # print(kgram)
            if (fc - BW / 2) <= 0:
                if (fc + BW / 2) >= int(fs/2):
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 4,
                                         'CutoffFrequency2', (fs/2)-1, 'SampleRate', srdo, nargout=1)
                else:
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 4,
                                         'CutoffFrequency2', fc + BW / 2, 'SampleRate', srdo, nargout=1)
            else:
                if (fc + BW / 2) >= (fs/2):
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 2,
                                         'CutoffFrequency2', (fs/2)-1, 'SampleRate', srdo, nargout=1)
                else:
                    bpf = eng.designfilt('bandpassfir', 'FilterOrder', 200.0, 'CutoffFrequency1', fc - BW / 2,
                                         'CutoffFrequency2', fc + BW / 2, 'SampleRate', srdo, nargout=1)

            xOuterBpf = eng.filter(bpf, gsdo, nargout=1)
            tmp = [[fc - BW / 2], [fc + BW / 2]]
            [pEnvOuterBpf, fEnvOuterBpf, xEnvOuterBpf, tEnvBpfOuter] = eng.envspectrum(gsdo, srdo, 'FilterOrder',
                                                                                       200.0, 'Band',
                                                                                       matlab.double(tmp),
                                                                                       nargout=4)

            tEnvOuter = [item for sublist in tEnvOuter for item in sublist]
            xEnvOuter = [item for sublist in xEnvOuter for item in sublist]
            # fEnvOuter = [item for sublist in fEnvOuter for item in sublist]
            # pEnvOuter = [item for sublist in pEnvOuter for item in sublist]
            sk = [item for sublist in sk for item in sublist]
            fout = [item for sublist in fout for item in sublist]
            xEnvOuterBpf = [item for sublist in xEnvOuterBpf for item in sublist]
            tEnvBpfOuter = [item for sublist in tEnvBpfOuter for item in sublist]
            pEnvOuterBpf = [item for sublist in pEnvOuterBpf for item in sublist]
            fEnvOuterBpf = [item for sublist in fEnvOuterBpf for item in sublist]

            for item in self.plot_7.items():
                if isinstance(item, pg.TextItem):
                    self.plot_7.removeItem(item)
            self.plot_7.clearPlots()

            for item in self.plot_8.items():
                if isinstance(item, pg.TextItem):
                    self.plot_8.removeItem(item)
            self.plot_8.clearPlots()

            # for item in self.plot_6.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_6.removeItem(item)
            # self.plot_6.clearPlots()

            for item in self.plot_21.items():
                if isinstance(item, pg.TextItem):
                    self.plot_21.removeItem(item)
            self.plot_21.clearPlots()

            for item in self.plot_22.items():
                if isinstance(item, pg.TextItem):
                    self.plot_22.removeItem(item)
            self.plot_22.clearPlots()

            for item in self.plot_23.items():
                if isinstance(item, pg.TextItem):
                    self.plot_23.removeItem(item)
            self.plot_23.clearPlots()

            self.plot_7.plot(lst,data.tolist(),
                             pen=pg.mkPen(pg.intColor(6), width=1))  # ,symbol='o', symbolSize=2
            self.plot_7.autoRange()

            self.plot_8.plot(tEnvOuter, xEnvOuter,
                             pen=pg.mkPen(pg.intColor(6), width=1))  # ,symbol='o', symbolSize=2
            self.plot_8.autoRange()

            self.plot_21.plot(fout, sk, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_21.autoRange()

            self.plot_22.plot(tEnvBpfOuter, xEnvOuterBpf, pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_22.autoRange()

            self.plot_23.plot(fEnvOuterBpf[0:2000], pEnvOuterBpf[0:2000], pen=pg.mkPen(pg.intColor(6), width=1))
            self.plot_23.autoRange()

            max_index = pEnvOuterBpf.index(max(pEnvOuterBpf))
            item = QtWidgets.QTableWidgetItem(str(round(fEnvOuterBpf[max_index], 2)))
            item.setForeground(QtGui.QBrush(QtCore.Qt.red))  # 设置字体颜色为红色
            font = QtGui.QFont()
            font.setPointSize(12)  # 设置字体大小为12
            font.setBold(True)  # 设置字体加粗
            item.setFont(font)  # 设置字体
            self.tableWidget_4.setItem(1, 13, item)
            # for i in mat_contents.keys():
            #     if 'time' in i:
            #         data = mat_contents[i]
            #         break
            # data = data.flatten().tolist()
            # fft_data = np.fft.fft(data)
            # freq = np.fft.fftfreq(len(data), d=1 / 12000)  # 采样频率为12000Hz
            #
            # for item in self.plot_7.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_7.removeItem(item)
            # self.plot_7.plot(data, pen=pg.mkPen(pg.intColor(6), width=2))
            # self.plot_7.autoRange()
            # for item in self.plot_8.items():
            #     if isinstance(item, pg.TextItem):
            #         self.plot_8.removeItem(item)
            # self.plot_8.plot(freq[:int(len(freq) / 2)], np.abs(fft_data)[:int(len(fft_data) / 2)],
            #                  pen=pg.mkPen(pg.intColor(6), width=2))
            # self.plot_8.autoRange()


def show(shared_data):
    app = QApplication(sys.argv)
    # 实例化页面并展示
    demo = DemoMain(shared_data)
    demo.show()
    sys.exit(app.exec_())


def getdata(shared_data):
    flag = 0
    while True:
        if shared_data['flag'][0] == 0:
            # if shared_data['flag'][1] != flag:
            #     RS485.restart(255, 3, 30, 10)
            #     flag = flag + 1
            data = RS485.communcation(1, 0, 22)
            shared_data['shard'] = data
            time.sleep(0.2)

        elif shared_data['flag'][0] == 1:
            # if shared_data['flag'][1] != flag:
            #     RS485.restart(255, 3, 30, 10)
            #     flag = flag + 1
            data = RS485.communcation(1, 23, 120)
            shared_data['shard'] = data
            time.sleep(0.3)

        elif shared_data['flag'][0] == 2:
            # print(shared_data['flag'])
            if shared_data['flag'][1] != flag:
                data = RS485.communcation_1024(shared_data['flag'][2])
                if len(data) == 10240:
                    shared_data['shard'] = data
                    time.sleep(0.3)
                    flag = flag + 1
            else:
                time.sleep(0.3)
                pass


if __name__ == '__main__':
    manager = Manager()
    ls = []
    ls_2 = [0, 0, 0]
    shared_data = manager.dict({'shard': ls, 'flag': ls_2})
    p1 = Process(target=show, args=(shared_data,))
    p2 = Process(target=getdata, args=(shared_data,))
    p1.start()
    p2.start()
    p1.join()
    p2.terminate()
