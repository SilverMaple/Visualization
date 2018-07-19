# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 14:07
# @Author  : SilverMaple
# @Site    : https://github.com/SilverMaple
# @File    : interact.py

from threading import _start_new_thread
from visualization import Network
from FR import FRLayout, FR3DLayout
import sys
from PyQt5.QtCore import Qt, QLineF, QRectF, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGraphicsView, QGraphicsScene, QGridLayout, \
    QMessageBox, QWidget, QPushButton, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QPen, QColor
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

POINT_SIZE = 10
APP_WIDTH = 1320
APP_HEIGHT = 500


class Point:
    def __init__(self, x, y, name, color=None):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.display = True


class Line:
    def __init__(self, a, b, color_index, color=None):
        self.a = a
        self.b = b
        self.color_index = color_index
        self.color = color
        self.display = True


class Messenger:
    def __init__(self):
        self.setupFlag = False
        self.statusBar = None

    def setup(self, statusBar):
        self.statusBar = statusBar
        self.setupFlag = True

    def changeStatusBar(self, content):
        try:
            if self.setupFlag:
                self.statusBar.showMessage(content)
        except Exception as e:
            print(e)


messenger = Messenger()


class PointButton(QPushButton):
    def __init__(self, ig, index, color, *args):
        QPushButton.__init__(self, *args)
        self.setMouseTracking(False)
        self.setStyleSheet(('''
        QPushButton{
        background-color: %s ;
        border-style: outset;
        border-width: 1px;
        border-radius: 5px;
        border-color: black;
        font: 1px;
        padding: 0px;
        }
        QPushButton:hover {
        background-color: yellow;
        border-style: inset;
        }
        QPushButton:pressed {
        background-color: rgb(224, 0, 0);
        border-style: inset;
        }
        QPushButton#cancel{
            background-color: red ;
        }
        ''') % color)
        self.color = color
        self.ig = ig
        self.index = index
        self.x = self.ig.points[index].x
        self.y = self.ig.points[index].y

    def restore(self):
        self.resize(10, 10)
        self.setWindowOpacity(1)

    def mouseMoveEvent(self, event):
        message = 'move event at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        messenger.changeStatusBar(message)

    def mouseReleaseEvent(self, event):
        message = 'release event at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())

        if event.pos().x() < 10 and event.pos().x() > 0 and event.pos().y() < 10 and event.pos().y() > 0:
            return
        x = self.pos().x() + event.pos().x()
        y = self.pos().y() + event.pos().y()
        # v, index = self.text()
        # print(self.accessibleName())
        # v, index = self.accessibleName()
        messenger.changeStatusBar(message)

    def dragMoveEvent(self, event):
        message = 'drag move at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        messenger.changeStatusBar(message)

    def dragLeaveEvent(self, event):
        message = 'drag leave at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        messenger.changeStatusBar(message)

    def mousePressEvent(self, event):
        message = 'press at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        # print('press at point[ ', self.text(), ' ]: ', event.pos().x(), event.pos().y())
        self.ig.points[self.index].display = False
        self.hide()
        vLineScene.leavePoint()
        vLineScene.updateScene()
        vpFrontView.update()
        messenger.changeStatusBar(message)

    def enterEvent(self, *args, **kwargs):
        message = 'Enter in point: ' + str(self.index + 1)
        vLineScene.focusPoint(self.index)
        messenger.changeStatusBar(message)

    def leaveEvent(self, *args, **kwargs):
        message = 'Leave in point: ' + str(self.index + 1)
        vLineScene.leavePoint()
        messenger.changeStatusBar(message)


class LineItem(QGraphicsLineItem):
    def __init__(self, ig, index, color, view, *args, **kwargs):
        # QGraphicsLineItem.__init__(*args, **kwargs)
        super().__init__(*args)
        self.ig = ig
        self.index = index
        self.view = view
        self.a = self.ig.lines[index].a
        self.b = self.ig.lines[index].b
        self.name = '-'.join([str(self.a), str(self.b)])
        self.color = color
        self.setZValue(-1)
        # 设置画笔
        pen = self.pen()
        p = QPen()
        pen.setColor(QColor(self.color))
        pen.setWidth(1)
        self.setPen(pen)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.setToolTip(self.name)

    def focus(self):
        pen = self.pen()
        pen.setWidth(2)
        self.setPen(pen)
        self.update()

    def restore(self):
        self.setOpacity(1)
        pen = self.pen()
        pen.setWidth(1)
        self.setPen(pen)
        self.update()

    def mousePressEvent(self, *args, **kwargs):
        self.ig.lines[self.index].display = False
        self.hide()
        self.view.update()
        vpFrontView.update()
        messenger.changeStatusBar('mousePress for:%s' % self.name)

    def hoverEnterEvent(self, *args, **kwargs):
        pen = self.pen()
        pen.setColor(QColor(Qt.yellow))
        self.setPen(pen)
        self.view.update()
        messenger.changeStatusBar('hoverEnter for:%s' % self.name)

    def hoverLeaveEvent(self, *args, **kwargs):
        pen = self.pen()
        pen.setColor(QColor(self.color))
        self.setPen(pen)
        self.view.update()
        messenger.changeStatusBar('hoverLeave for:%s' % self.name)


class ResultPainter(QWidget):
    def __init__(self, ig, *args):
        super().__init__(*args)
        self.ig = ig
        self.entropy = None
        self.trigger = False
        self.initUI()

    def initUI(self):
        # self.setGeometry(400, 300, 280, 170)
        # self.setMinimumSize(300, 300)
        self.setWindowTitle('绘制点')
        self.resize(300, 500)
        self.show()
        self.entropy = self.ig.network.get_entropy()
        for i in range(len(self.entropy)):
            self.entropy[i] = float(self.entropy[i].replace('\n', ''))

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def triggerUpdate(self):
        self.trigger = True
        pass

    def draw(self, qp):
        index = 0
        for i in range(len(self.entropy)):
            pen = QPen(QColor(self.ig.colors[i]), 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(5, index * 20 + 20, "●")
            pen = QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(20, index * 20 + 20, "社区%s的信息熵：%f" % (str(index + 1), self.entropy[i]))
            index += 1
        qp.drawText(15, (index + 1) * 20, "信息熵的总和：%f" % sum([i for i in self.entropy]))

        if self.trigger:
            qp.drawText(15, 200, "输出：%f" % sum([i for i in self.entropy]))


class NetworkView(QGraphicsView):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.m_translateButton = Qt.LeftButton
        self.m_scale = 1.0
        self.m_zoomDelta = 0.1
        self.m_translateSpeed = 2.0
        self.m_bMouseTranslate = False
        self.m_lastMousePos = None

        self.setRenderHint(QPainter.Antialiasing)

        self.setSceneRect(0, 0, 500, 500)
        self.centerOn(0, 0)

    # 平移速度
    def setTranslateSpeed(self, speed):
        # 建议速度范围
        assert speed >= 0.0 and speed <= 2.0, "self.setTranslateSpeed: Speed should be in range [0.0, 2.0]."
        self.m_translateSpeed = speed

    def translateSpeed(self):
        return self.m_translateSpeed

    # 缩放的增量
    def setZoomDelta(self, delta):
        # 建议增量范围
        assert delta >= 0.0 and delta <= 1.0, "self.setZoomDelta: Delta should be in range [0.0, 1.0]."
        self.m_zoomDelta = delta

    def zoomDelta(self):
        return self.m_zoomDelta

    # 上 / 下 / 左 / 右键向各个方向移动、加 / 减键进行缩放、空格 / 回车键旋转
    def keyPressEvent(self, event):
        messenger.changeStatusBar('Key pressed: %s' % event.key())
        # 使用==不能用is，因为类型不同值相同
        if event.key() == Qt.Key_Up:
            self.translate(0, -2)  # 上移
        elif event.key() == Qt.Key_Down:
            self.translate(0, 2)  # 下移
        elif event.key() == Qt.Key_Left:
            self.translate(-2, 0)  # 左移
        elif event.key() == Qt.Key_Right:
            self.translate(2, 0)  # 右移
        elif event.key() == Qt.Key_Plus:
            self.zoomIn()  # 放大
        elif event.key() == Qt.Key_Minus:
            self.zoomOut()  # 缩小
        elif event.key() == Qt.Key_Space:
            self.rotate(-5)  # 逆时针旋转
        elif event.key() == Qt.Key_Enter \
                or event.key() == Qt.Key_Return:
            self.rotate(5)
        else:
            super().keyPressEvent(event)

    # 平移
    def mouseMoveEvent(self, event):
        messenger.changeStatusBar('Mouse move: %s' % str(event.pos()))
        if self.m_bMouseTranslate:
            mouseDelta = self.mapToScene(event.pos()) - self.mapToScene(self.m_lastMousePos)
            self.translate(mouseDelta.x(), mouseDelta.y())

        self.m_lastMousePos = event.pos()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        messenger.changeStatusBar('Mouse press: %s' % str(event.pos()))
        if event.button() == self.m_translateButton:
            # 当光标底下没有item时，才能移动
            point = self.mapToScene(event.pos())
            if self.scene().itemAt(point, self.transform()) is None:
                self.m_bMouseTranslate = True
                self.m_lastMousePos = event.pos()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        messenger.changeStatusBar('Mouse release: %s' % str(event.pos()))
        if event.button() == self.m_translateButton:
            self.m_bMouseTranslate = False

        super().mouseReleaseEvent(event)

    # 放大 / 缩小
    def wheelEvent(self, event):
        # 滚轮的滚动量
        scrollAmount = event.angleDelta()
        # 正值表示滚轮远离使用者（放大），负值表示朝向使用者（缩小）
        if scrollAmount.y() > 0:
            self.zoomIn()
            messenger.changeStatusBar('Zoom in: %s' % str(self.m_zoomDelta))
        else:
            self.zoomOut()
            messenger.changeStatusBar('Zoom out: %s' % str(self.m_zoomDelta))

    # 放大
    def zoomIn(self):
        self.zoom(1 + self.m_zoomDelta)

    # 缩小
    def zoomOut(self):
        self.zoom(1 - self.m_zoomDelta)

    # 缩放 - scaleFactor：缩放的比例因子
    def zoom(self, scaleFactor):
        # 防止过小或过大
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)
        self.m_scale *= scaleFactor
        # 缩放，可有可无
        # if self.m_scale > 1:
        #     try:
        #         for i in vLineScene.buttons:
        #             i.resize(10-(self.m_scale-1)/2, 10-(self.m_scale-1)/2)
        #             i.move(i.x + self.m_scale/4, i.y + self.m_scale/4)
        #     except Exception as e:
        #         print(e)

    # 平移
    def translate(self, x, y):
        messenger.changeStatusBar('Translate: %s' % str((x, y)))
        delta = QPoint(x, y)
        # 根据当前zoom缩放平移数
        delta *= self.m_scale
        delta *= self.m_translateSpeed

        # super().translate(x, y)
        # super().translate(delta.x(), delta.y())

        # view根据鼠标下的点作为锚点来定位scene
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        newCenter = QPoint(self.viewport().rect().width() / 2 - delta.x(),
                           self.viewport().rect().height() / 2 - delta.y())
        self.centerOn(self.mapToScene(newCenter))

        # scene在view的中心点作为锚点
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)


class NetworkScene(QGraphicsScene):
    def __init__(self, ig, *__args):
        super().__init__(*__args)
        self.ig = ig
        self.buttons = []
        for i in range(len(self.ig.points)):
            b = PointButton(self.ig, i, self.ig.points[i].color)
            # b = PointButton(str(self.ig.points[i].name))
            b.setToolTip(str(self.ig.points[i].name))
            b.move(self.ig.points[i].x, self.ig.points[i].y)
            b.resize(POINT_SIZE, POINT_SIZE)
            # b.setParent(self)
            self.addWidget(b)
            b.show()
            b.setAttribute(Qt.WA_TranslucentBackground, True)
            self.buttons.append(b)

        self.lineItem = []
        for i in range(len(self.ig.lines)):
            # 初始化默认显示所有
            x = self.ig.points[self.ig.lines[i].a - 1].x + POINT_SIZE / 2
            y = self.ig.points[self.ig.lines[i].a - 1].y + POINT_SIZE / 2
            x1 = self.ig.points[self.ig.lines[i].b - 1].x + POINT_SIZE / 2
            y1 = self.ig.points[self.ig.lines[i].b - 1].y + POINT_SIZE / 2

            pItem = LineItem(self.ig, i, self.ig.lines[i].color, self)
            # 设置直线位于(x1, y1)和(x2, y2)之间
            pItem.setLine(QLineF(x, y, x1, y1))
            self.lineItem.append(pItem)
            pItem.isVisible()
            # 将item添加至场景中
            self.addItem(pItem)

    def reload(self):
        for i in range(len(self.ig.points)):
            self.buttons[i].move(self.ig.points[i].x, self.ig.points[i].y)

        for i in range(len(self.ig.lines)):
            # 初始化默认显示所有
            x = self.ig.points[self.ig.lines[i].a - 1].x + POINT_SIZE / 2
            y = self.ig.points[self.ig.lines[i].a - 1].y + POINT_SIZE / 2
            x1 = self.ig.points[self.ig.lines[i].b - 1].x + POINT_SIZE / 2
            y1 = self.ig.points[self.ig.lines[i].b - 1].y + POINT_SIZE / 2
            self.lineItem[i].setLine(QLineF(x, y, x1, y1))
        self.restoreScene()

    def focusPoint(self, index):
        for b in self.buttons:
            b.setWindowOpacity(.3)
            b.resize(10, 10)

        self.buttons[index].setWindowOpacity(1)
        self.buttons[index].resize(15, 15)
        for line in self.lineItem:
            if line.a == index + 1 or line.b == index + 1:
                line.setOpacity(1)
                line.focus()
            else:
                line.restore()
                line.setOpacity(.3)

    def leavePoint(self):
        for i in range(len(self.buttons)):
            self.buttons[i].restore()

        for i in range(len(self.lineItem)):
            self.lineItem[i].restore()

    def restoreScene(self):
        for i in range(len(self.buttons)):
            self.buttons[i].show()
            self.buttons[i].restore()
            self.ig.points[i].display = True

        for i in range(len(self.lineItem)):
            self.lineItem[i].show()
            self.lineItem[i].restore()
            self.ig.lines[i].display = True

        vpFrontView.update()

    def updateScene(self):
        index = 0
        shift = 10
        length = len(self.ig.points)
        for i in range(length):
            if self.ig.points[i].display:
                x = self.ig.points[i].x
                y = self.ig.points[i].y

                # qp.drawPoint(x, y)
                # qp.drawText(x + shift, y + shift, str(self.ig.points[i].name))
                index += 1
            elif self.buttons[i].isVisible:
                self.buttons[i].setVisible(False)
                self.update()

        length = len(self.ig.lines)
        for i in range(length):
            if not self.ig.lines[i].display and self.lineItem[i].isVisible():
                self.lineItem[i].setVisible(False)
                continue
            elif self.ig.lines[i].display and not self.lineItem[i].isVisible():
                self.lineItem[i].setVisible(True)
            if self.ig.points[self.ig.lines[i].a - 1].display and self.ig.points[self.ig.lines[i].b - 1].display \
                    and self.ig.lines[i].display:
                x = self.ig.points[self.ig.lines[i].a - 1].x + POINT_SIZE / 2
                y = self.ig.points[self.ig.lines[i].a - 1].y + POINT_SIZE / 2
                x1 = self.ig.points[self.ig.lines[i].b - 1].x + POINT_SIZE / 2
                y1 = self.ig.points[self.ig.lines[i].b - 1].y + POINT_SIZE / 2
                # qp.drawLine(x, y, x1, y1)
            else:
                self.ig.lines[i].display = False
                self.lineItem[i].setVisible(False)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        self.restoreScene()


class ViewPainter(QWidget):
    def __init__(self, ig):
        super().__init__()
        self.ig = ig
        self.initUI()

    def initUI(self):
        self.setWindowTitle('绘制点')
        self.resize(500, 500)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        qp.setPen(QtCore.Qt.red)
        size = self.size()
        length = len(self.ig.points)
        pos = []

        index = 0
        shift = 10
        for i in range(length):
            if self.ig.points[i].display:
                x = self.ig.points[i].x
                y = self.ig.points[i].y

                # qp.drawPoint(x, y)
                qp.drawText(x + shift, y + shift, str(self.ig.points[i].name))
                pos.append([x, y])
                index += 1

        length = len(self.ig.lines)
        pen = QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)

        for i in range(length):
            if False:
                pen.setStyle(QtCore.Qt.DashLine)
            else:
                pen.setStyle(QtCore.Qt.SolidLine)
            pen = QPen(QColor(self.ig.lines[i].color), 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)

            if self.ig.points[self.ig.lines[i].a - 1].display and self.ig.points[self.ig.lines[i].b - 1].display \
                    and self.ig.lines[i].display:
                x = self.ig.points[self.ig.lines[i].a - 1].x + POINT_SIZE / 2
                y = self.ig.points[self.ig.lines[i].a - 1].y + POINT_SIZE / 2
                x1 = self.ig.points[self.ig.lines[i].b - 1].x + POINT_SIZE / 2
                y1 = self.ig.points[self.ig.lines[i].b - 1].y + POINT_SIZE / 2
                qp.drawLine(x, y, x1, y1)

        if self.ig.threadDone:
            self.ig.threadDone = False
            vLineScene.reload()
            vLineView.update()
            message = 'Fruchterman-Reingold布局完成'
            messenger.changeStatusBar(message)


class InteractGraph(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.network = None
        self.threadDone = False
        self.readPoint()
        self.readLine()
        self.initNetwork()
        self.initUI()

    def initNetwork(self):
        self.network = Network()
        self.network.import_network_information()
        self.network.set_community_member()

    def initUI(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("程序主窗口")

        self.file_menu = QMenu('&文件', self)
        self.file_menu.addAction('&打开', self.loadData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&重新布局', self.reloadLayout,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.file_menu.addAction('&还原', self.restoreData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_D)
        self.file_menu.addAction('&退出', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.menuBar().addSeparator()
        self.menuBar().addAction('&打开', self.loadData)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&重新布局', self.reloadLayout)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&还原', self.restoreData)
        self.menuBar().addSeparator()

        self.menuBar().addAction('&帮助', self.about)

        self.main_widget = QWidget(self)

        l = QGridLayout(self.main_widget)

        global vLineView
        global vLineScene
        global vpFrontView

        # 为视图设置场景
        vLineView = NetworkView()
        # vLineView = QGraphicsView()
        vLineView.setStyleSheet("border:none; background:transparent;")
        vLineScene = NetworkScene(self)
        # vLineScene = QGraphicsScene()
        vLineView.setScene(vLineScene)
        vLineView.setMinimumSize(500, 500)
        vLineView.setRenderHint(QPainter.Antialiasing)

        vpFrontView = ViewPainter(self)
        vpResultView = ResultPainter(self)
        v3DView = self.get3DView()
        # v3DView.setAutoBufferSwap(False)
        v3DView.show()

        self.vpViews = [vpFrontView, vpResultView, vLineView]
        # self.vpViews = [vpFrontView, vLineView]

        self.graphicViews = []
        for i in range(len(self.vpViews)):
            self.graphicViews.append(QGraphicsView(self.main_widget))
            graphScene = QGraphicsScene()
            graphScene.addWidget(self.vpViews[i])
            self.graphicViews[i].setScene(graphScene)
            self.graphicViews[i].setAlignment(Qt.AlignCenter)
            self.graphicViews[i].verticalScrollBar().hide()
            self.graphicViews[i].horizontalScrollBar().hide()
            self.graphicViews[i].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.graphicViews[i].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.graphicViews[i].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # self.graphicViews[i].setMinimumSize(500, 300)
            l.addWidget(self.graphicViews[i], 0, i)

        # l.addWidget(self.graphicViews[0], 0, 0)
        # l.addWidget(self.graphicViews[1], 0, 1)
        # l.addWidget(self.graphicViews[2], 0, 2)
        # l.addWidget(self.graphicViews[3], 0, 3)

        self.gridLayout = l

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setMinimumSize(APP_WIDTH, APP_HEIGHT)
        # 状态条显示2秒
        self.statusBar().showMessage("就绪")
        messenger.setup(self.statusBar())
        self.center()

    def get3DView(self):
        w = gl.GLViewWidget()
        w.opts['distance'] = 20
        w.show()
        w.setWindowTitle('Network 3D Graph')

        g = gl.GLGridItem()
        w.addItem(g)
        colors = []
        fr = FR3DLayout()
        points = fr.outputLayout()
        print(points)
        # Gradient = A + (B - A) * N / Step
        # colorA = (1, 0, 0)
        # colorB = (0, 0, 1)
        # for i in range(1, 10):
        #     a = colorA[0] + (colorB[0] - colorA[0]) * i / 10.0
        #     b = colorA[1] + (colorB[1] - colorA[1]) * i / 10.0
        #     c = colorA[2] + (colorB[2] - colorA[2]) * i / 10.0
        #     colors.append((a, b, c, 0.8))
        colors = [(1, 0, 0, .8), (0, 1, 0, .8), (0, 0, 1, .8),
                  (1, 1, 0, .8), (1, 0, 1, .8), (0, 1, 1, .8)]

        pos = np.empty((105, 3))
        size = np.empty(105)
        color = np.empty((105, 4))
        for i in range(len(self.points)):
            pos[i] = ((points[i+1][0] - 1700)/300.0,
                      (points[i+1][1]-1700)/300.0,
                      (points[i+1][2]-200)/300.0)
            size[i] = 0.01
            color[i] = colors[self.colors.index(self.points[i].color)]
            # print(color[i])

        sp1 = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        sp1.translate(5, 5, 0)
        n = 51

        for i in range(len(self.lines)):
            x = [pos[self.lines[i].a-1][0], pos[self.lines[i].b-1][0]]
            y = [pos[self.lines[i].a-1][1], pos[self.lines[i].b-1][1]]
            z = [pos[self.lines[i].a-1][2], pos[self.lines[i].b-1][2]]
            tmp = None
            if self.lines[i].color in self.colors:
                tmp = colors[self.colors.index(self.lines[i].color)]
            else:
                tmp = (1, 1, 1, 0.8)

            pts = np.vstack([x, y, z]).transpose()
            plt = gl.GLLinePlotItem(pos=pts, color=tmp, width=.5, antialias=True)
            plt.translate(5, 5, 0)
            w.addItem(plt)

        w.addItem(sp1)
        return w

    def center(self):  # 主窗口居中显示函数
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.move((screen.width() - APP_WIDTH) / 2, (screen.height() - APP_HEIGHT) / 2)

    def reloadLayout(self):
        message = 'Fruchterman-Reingold重新布局中...'
        messenger.changeStatusBar(message)
        # 创建两个线程
        try:
            _start_new_thread(self.reloadLayoutThread, (self,))
        except Exception as e:
            print("Error: unable to start thread")
            message = 'Fruchterman-Reingold布局失败！'
            messenger.changeStatusBar(message)
            print(e)

    def reloadLayoutThread(self, useless):
        fr = FRLayout()
        fr.outputLayout()
        self.readPoint()
        self.threadDone = True
        messenger.changeStatusBar('')
        vpFrontView.update()
        # vLineScene.reload()
        # vLineView.update()

    def about(self):
        QMessageBox.about(self, "帮助",
                          """
    1.	信息熵可视化程序主要功能如下：
    a)	生成数据集网络图
    b)	提供节点、边交互功能
    C)	计算信息熵与生成相应图表
    2. 按键功能说明：
    Ctrl   +   O: 打开数据文件 //未涉及
    Ctrl   +   D: 还原当前数据
    Ctrl   +   S: 保存当前数据 //未涉及
    Wheel   Up：放大
    Wheel Down：缩小
    Enter       ：顺势针旋转
    Space       ：逆时针旋转
    Double Click：还原当前数据
    3. 面板说明：
    左视图：不可交互
    中视图：信息熵结果展示与操作区域
    右试图：交互面板
    4. 程序代码可在以下地址获取：
    https://github.com/SilverMaple/Visualization
        """
                          )

    def loadData(self):
        pass

    def saveData(self):
        # save as a graph
        pass

    @staticmethod
    def restoreData():
        vLineScene.restoreScene()

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def readPoint(self):
        pointsLines = open('../R_script/points.txt').readlines()
        self.points = []
        self.colors = []
        for line in pointsLines:
            try:
                a, b, c = line.strip().replace('"', '').split()
                c = c[:-2]
                if c not in self.colors:
                    self.colors.append(c)
                self.points.append(Point(float(a), float(b), len(self.points) + 1, color=c))
            except Exception as e:
                print(e)

    def readLine(self):
        lineLines = open('../R_script/lines.txt').readlines()
        self.lines = []
        for line in lineLines:
            try:
                a, b, c, d = line.strip().replace('"', '').split()
                d = d[:-2]
                self.lines.append(Line(int(a), int(b), int(c), color=d))
            except Exception as e:
                print(e)

    def updateGraph(self):
        pass

    def showData(self):
        print("Points Length: ", len(self.points))
        for p in self.points:
            print("Point:", ' '.join([str(p.name), str(p.x), str(p.y), p.color]))

        print("Lines Length: ", len(self.lines))
        for l in self.lines:
            print("Lines:", ' '.join([str(l.a), str(l.b), str(l.color_index), l.color]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # a = ViewNameLabel(text="here")
    ig = InteractGraph()
    ig.setWindowTitle("信息熵可视化")
    # ig.showData()
    ig.show()
    # sys.exit(qApp.exec_())
    app.exec_()
