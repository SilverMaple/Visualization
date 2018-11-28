# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 14:07
# @Author  : SilverMaple
# @Site    : https://github.com/SilverMaple
# @File    : interact.py

# import warnings
# warnings.simplefilter("error")
from threading import _start_new_thread
from visualization import Network, Community, COMMUNITY_FILE, NETWORK_FILE
from FR import FRLayout, FR3DLayout
from KK import KKLayout
import sys
import os
from PyQt5.QtCore import Qt, QLineF, QRectF, QPoint, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGraphicsView, QGraphicsScene, QGridLayout, \
    QMessageBox, QWidget, QPushButton, QGraphicsLineItem, QLabel, QAction, QShortcut, QInputDialog, QLineEdit
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QMouseEvent, QIcon, QKeySequence, QPalette, QBrush, QPixmap
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import matplotlib.pyplot as plt
import numpy as np

POINT_SIZE = 10
APP_WIDTH = 1320
APP_HEIGHT = 500
ICON_PATH = 'c_plus/select.ico'


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


class IconManager():

    def __init__(self):
        pass

    def generateIcon(self, colorDict=None):
        colorDict = {'red': 5, 'blue': 2, 'green': 3}
        # data = np.random.randint(1, 11, 5)

        plt.pie(colorDict.values(), colors=colorDict.keys())
        plt.axis('equal')
        # plt.axis('off')
        # fig = plt.gcf()
        # plt.gca().xaxis.set_major_locator(plt.NullLocator())
        # plt.gca().yaxis.set_major_locator(plt.NullLocator())
        # plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
        # plt.margins(0,0)
        # fig.savefig('a.png', format='png', transparent=True, dpi=10, pad_inches = 0)
        plt.savefig('a.svg', dpi=10, pad_inches=0, transparent=True)

    def getIcon(self, index):
        pass


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


class ActionButton(QPushButton):
    def __init__(self, ci, index, ofCommunity,  *__args):
        super().__init__(*__args)
        self.ci = ci
        self.index = index
        self.ofCommunity = ofCommunity

    def mousePressEvent(self, event):
        ci = self.ci
        print('changeCommunity: ', ci)
        if ci == self.ofCommunity:
            return
        else:
            tempCommunity = {'index': self.index, 'from': self.ofCommunity, 'to': ci}
            vpResultView.updateEntropy(community=tempCommunity)


class PointButton(QPushButton):
    def __init__(self, ig, index, color, *args):
        QPushButton.__init__(self, *args)
        self.setMouseTracking(True)
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
        self.changeColor = None
        self.ig = ig
        self.index = index
        self.x = self.ig.points[index].x
        self.y = self.ig.points[index].y
        self.dragging = False
        self.ofCommunity = None
        for ci in range(len(self.ig.network.communities)):
            if index+1 in self.ig.network.communities[ci].vertexes:
                self.ofCommunity = ci
                break
        self.selectedCommunity = self.ofCommunity
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        # self.customContextMenuRequested.connect(self.showContextMenu)
        self.contextMenu = QMenu(self)
        # self.contextMenu.addSection()
        # self.communityMenu = self.contextMenu.addMenu('移动至社区')
        for ci in range(len(self.ig.network.communities)):
            tempAction = self.contextMenu.addAction("社区%d" % (ci+1))
            tempAction.triggered.connect(lambda: self.changeCommunity(ci))
        self.contextMenuState = False

    def changeCommunity(self, ci):
        # 直接使用坐标计算选择社区，以后有修改方法后再改
        ci = int(((QCursor.pos().y() - self.menuPos.y())-2) / 23)
        if ci == self.selectedCommunity:
            return
        # elif ci == self.ofCommunity:
        #     self.changeColor = None
        #     self.restore()
        #     self.ig.points[self.index].display = True
        #     self.update()
        #     print('here')
        #     tempCommunity = {'index': self.index, 'from': self.ofCommunity, 'to': ci}
        #     vpResultView.updateEntropy(community=tempCommunity)
        else:
            self.selectedCommunity = ci
            self.changeColor = self.ig.colors[ci]
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
            ''') % self.changeColor)
            for line in vLineScene.lineItem:
                anotherPoint = None
                if line.a == self.index+1:
                    anotherPoint = line.b
                elif line.b == self.index+1:
                    anotherPoint = line.a
                else:
                    continue
                if self.ig.points[anotherPoint-1].color == self.changeColor:
                    line.setColor(self.changeColor)
                    line.changeColor = self.changeColor
                else:
                    line.setColor('#000000')
                    line.changeColor = '#000000'
            if ci == self.ofCommunity:
                self.changeColor = None
            self.update()
            tempCommunity = {'index': self.index, 'from': self.ofCommunity, 'to': ci}
            vpResultView.updateEntropy(community=tempCommunity)

    def showContextMenu(self, pos):
        self.menuPos = QCursor.pos()
        # 菜单显示前，将它移动到鼠标点击的位置
        for i in range(len(self.contextMenu.actions())):
            if self.selectedCommunity == i:
                self.contextMenu.actions()[i].setIconText('✔')
                self.contextMenu.actions()[i].setIcon(QIcon(ICON_PATH))
                self.contextMenu.actions()[i].setIconVisibleInMenu(True)
            else:
                self.contextMenu.actions()[i].setIconText('')
                self.contextMenu.actions()[i].setIconVisibleInMenu(False)
        self.contextMenu.exec(QCursor.pos())  # 在鼠标位置显示
        # self.contextMenu.show()

    def restore(self, saveColor=None):
        if not saveColor and self.changeColor:
            self.changeColor = None
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
                ''') % self.color)
        self.resize(10, 10)
        self.setWindowOpacity(1)

    def mouseMoveEvent(self, event):
        if self.dragging:
            message = 'move event at point[ ' + str(self.index+1) + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
            x = self.pos().x() + event.pos().x()
            y = self.pos().y() + event.pos().y()
            self.ig.points[self.index].x = x
            self.ig.points[self.index].y = y
            self.move(x, y)
            for l in vLineScene.lineItem:
                if l.a == self.index+1 or l.b == self.index+1:
                    x = self.ig.points[l.a - 1].x + POINT_SIZE / 2
                    y = self.ig.points[l.a - 1].y + POINT_SIZE / 2
                    x1 = self.ig.points[l.b - 1].x + POINT_SIZE / 2
                    y1 = self.ig.points[l.b - 1].y + POINT_SIZE / 2
                    # 设置直线位于(x1, y1)和(x2, y2)之间
                    l.setLine(QLineF(x, y, x1, y1))
            # vLineView.update()
            vpFrontView.update()

            messenger.changeStatusBar(message)

    def mouseReleaseEvent(self, event):
        message = 'release event at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())

        if event.pos().x() < 10 and event.pos().x() > 0 and event.pos().y() < 10 and event.pos().y() > 0:
            return
        x = self.pos().x() + event.pos().x()
        y = self.pos().y() + event.pos().y()
        self.dragging = False
        # v, index = self.text()
        # print(self.accessibleName())
        # v, index = self.accessibleName()
        messenger.changeStatusBar(message)

    def dragMoveEvent(self, event):
        message = 'drag move at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        print(message)
        messenger.changeStatusBar(message)

    def dragLeaveEvent(self, event):
        message = 'drag leave at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
        print(message)
        messenger.changeStatusBar(message)

    def mousePressEvent(self, event):
        if Qt.MiddleButton == event.button():
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
            background-color: %s;
            border-style: inset;
            }
            QPushButton:pressed {
            background-color: rgb(224, 0, 0);
            border-style: inset;
            }
            QPushButton#cancel{
                background-color: red ;
            }
            ''') % (self.color, self.color))
            self.leaveEvent(event)
            vpResultView.updateEntropy(dot=self.index)
            message = 'press at point[ ' + self.text() + ' ]: ' + str(event.pos().x()) + ' ' + str(event.pos().y())
            # print('press at point[ ', self.text(), ' ]: ', event.pos().x(), event.pos().y())
            self.ig.points[self.index].display = False
            self.hide()
            vLineScene.leavePoint()
            vLineScene.updateScene()
            vpFrontView.update()
            messenger.changeStatusBar(message)
        elif Qt.RightButton == event.button():
            self.showContextMenu(event.pos())
        elif Qt.LeftButton == event.button():
            self.dragging = True


    def enterEvent(self, *args, **kwargs):
        if self.changeColor:
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
            ''') % self.changeColor)
        else:
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
            ''') % self.color)
        inLineSum = 0
        outLineSum = 0
        regionCount = {c: 0 for c in self.ig.colors}
        for i in range(len(self.ig.lines)):
            if self.ig.lines[i].display and \
                    (self.ig.lines[i].a == self.index+1 or self.ig.lines[i].b == self.index+1):
                if vLineScene.lineItem[i].getCurrentColor() == self.getCurrentColor():
                    inLineSum += 1
                else:
                    outLineSum += 1
                    if self.ig.lines[i].a == self.index + 1:
                        anotherPoint = self.ig.lines[i].b
                    else:
                        anotherPoint = self.ig.lines[i].a
                    color = vLineScene.buttons[anotherPoint - 1].getCurrentColor()
                    regionCount[color] += 1
        regionCount = {c: regionCount[c] for c in regionCount if regionCount[c] != 0}
        regionString = '\n' + '\n'.join(['  Community {}: {}'.format(self.ig.colors.index(c)+1, regionCount[c])
                                         for c in regionCount])
        self.setToolTip('Point: ' + str(self.index+1) + '\nInside: ' + str(inLineSum) +
                        '\nOutside: ' + str(outLineSum) + regionString)
        message = 'Enter in point: ' + str(self.index + 1) + \
                  ' InLine sum: ' + str(inLineSum) + ' OutLine sum: ' + str(outLineSum) + regionString.replace('\n', '')
        vLineScene.focusPoint(self.index)
        messenger.changeStatusBar(message)

    def leaveEvent(self, *args, **kwargs):
        message = 'Leave in point: ' + str(self.index + 1)
        self.dragging = False
        vLineScene.leavePoint(saveColor=True)
        messenger.changeStatusBar(message)

    def getCurrentColor(self):
        if self.changeColor is None:
            return self.color
        return self.changeColor

    def getGlobalPos(self):
        return self.mapToParent(self.pos())
        # return self.mapToGlobal(self.pos())


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
        self.changeColor = None
        self.width = 1
        self.setZValue(-1)
        # 设置画笔
        pen = self.pen()
        p = QPen()
        pen.setColor(QColor(self.color))
        # print(self.color, self.width)
        pen.setWidth(self.width)
        self.setPen(pen)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.setToolTip(self.name)

    def setColor(self, color):
        pen = self.pen()
        p = QPen()
        pen.setColor(QColor(color))
        self.setPen(pen)
        self.update()

    def getCurrentColor(self):
        if self.changeColor is None:
            return self.color
        return self.changeColor

    def focus(self):
        pen = self.pen()
        pen.setWidth(2)
        self.setPen(pen)
        self.update()

    def restore(self, saveColor=None):
        self.setOpacity(1)
        pen = self.pen()
        if not saveColor:
            self.changeColor = None
            pen.setColor(QColor(self.color))
        pen.setWidth(self.width)
        self.setPen(pen)
        self.update()

    def mousePressEvent(self, *args, **kwargs):
        self.hoverLeaveEvent(*args, **kwargs)
        vpResultView.updateEntropy(pair=(self.a, self.b))
        self.ig.lines[self.index].display = False
        self.hide()
        self.view.update()
        vpFrontView.update()
        vpResultView.update()
        messenger.changeStatusBar('mousePress for:%s' % self.name)

    def hoverEnterEvent(self, *args, **kwargs):
        pen = self.pen()
        pen.setColor(QColor(Qt.yellow))
        self.setPen(pen)
        self.view.update()
        messenger.changeStatusBar('hoverEnter for:%s' % self.name)

    def hoverLeaveEvent(self, *args, **kwargs):
        pen = self.pen()
        if self.changeColor:
            pen.setColor(QColor(self.changeColor))
        else:
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
        self.descLabel = None
        self.isRemoveDots = False
        self.isRemovePairs = False
        self.isChangeCommunity = False
        self.dots = []
        self.pairs = []
        self.changeSets = []
        self.communities = []
        self.initUI()

    def initUI(self):
        self.resize(300, 500)
        self.hide()
        self.descLabel = QLabel(self)
        self.descLabel.setGeometry(20, 380, 260, 400)
        self.descLabel.setText("说明：\n"
                               "    鼠标悬停在点上的时候，第一个数字表示该节点的标识，第二个数字表示该节点与社区内节点的链接数目，"
                               "第三个数字表示该节点与其他社区节点的链接数目。"
                               "比如：59，6，4表示节点59与社区内节点的链接数目为6，与社区间其他节点的链接数目为4。")
        self.descLabel.setWordWrap(True)
        self.descLabel.setAlignment(Qt.AlignTop)
        self.descLabel.show()
        self.entropy = self.ig.network.get_entropy()
        self.staticEntropy = self.entropy
        for i in range(len(self.entropy)):
            self.entropy[i] = float(self.entropy[i].replace('\n', ''))

    def updateEntropy(self, pair=None, community=None, dot=None):
        tempPair = None
        tempCommunity = None
        tempDot = None
        print('----------------Update entropy----------------')

        # 删除边
        if pair is not None:
            self.isRemovePairs = True
            self.pairs.append(pair)
            tempPair = self.pairs
            if self.dots != []:
                tempDot = self.dots
        # 删除点和与其相连的边
        if dot is not None:
            dot += 1
            self.isRemoveDots = True
            for i in self.ig.lines:
                if dot == i.a or dot == i.b:
                    self.pairs.append((i.a, i.b))
            tempPair = self.pairs
            self.dots.append(dot)
            tempDot = self.dots

        self.communities = []
        # 删除点需重写社区划分信息
        if tempDot is not None:
            index = 0
            # self.communities = []
            if self.isChangeCommunity and community is None:
                fromIndex = []
                toIndex = []
                pointIndex = []
                for c in self.changeSets:
                    fromIndex.append(c['from'])
                    toIndex.append(c['to'])
                    pointIndex.append(c['index'])
                # 如果未修改过社区划分信息，则重新赋值
                if self.communities == []:
                    index = 0
                    for c in self.ig.network.communities:
                        self.communities.append([])
                        for v in c.vertexes:
                            self.communities[index].append(v)
                        index += 1
                for index in range(len(pointIndex)):
                    print('move point %d from community %d to community %d'
                          % (pointIndex[index] + 1, fromIndex[index], toIndex[index]))
                    self.communities[fromIndex[index]].remove(pointIndex[index] + 1)
                    self.communities[toIndex[index]].append(pointIndex[index] + 1)
                for j in range(len(self.communities)):
                    for v in self.communities[j]:
                        if v in tempDot:
                            self.communities[j].remove(v)
                            print('remove point: ', v)
                    index += 1
            else:
                for c in self.ig.network.communities:
                    self.communities.append([])
                    for v in c.vertexes:
                        if v not in tempDot:
                            self.communities[index].append(v)
                        else:
                            print('remove point: ', v)
                    index += 1
            # remove empty array
            while [] in self.communities:
                self.communities.remove([])
            tempCommunity = []
            for c in self.communities:
                tempCommunity.append('  '.join([str(i) for i in c]))
            if tempCommunity == []:
                tempCommunity = None

        if community is not None:
            if pair is None and self.pairs != []:
                tempPair = self.pairs
            if dot is None and self.dots != []:
                for i in self.dots:
                    print('remove point:', i)
            self.isChangeCommunity = True
            # 注意同一个点不应该重复移动
            removeItem = None
            for i in self.changeSets:
                # print(i['index'], community['index'])
                if i['index'] == community['index']:
                    removeItem = i
                    break
            if removeItem is not None:
                # print('remove duplicate item')
                self.changeSets.remove(removeItem)
            self.changeSets.append(community)
            fromIndex = []
            toIndex = []
            pointIndex = []
            for c in self.changeSets:
                fromIndex.append(c['from'])
                toIndex.append(c['to'])
                pointIndex.append(c['index'])
            # 如果未修改过社区划分信息，则重新赋值
            if self.communities == []:
                index = 0
                for c in self.ig.network.communities:
                    self.communities.append([])
                    for v in c.vertexes:
                        if self.dots == [] or self.dots != [] and v not in self.dots:
                            self.communities[index].append(v)
                    index += 1
            for index in range(len(pointIndex)):
                if self.dots != [] and pointIndex[index]+1 in self.dots:
                    continue
                print('move point %d from community %d to community %d'
                      % (pointIndex[index]+1, fromIndex[index], toIndex[index]))
                self.communities[fromIndex[index]].remove(pointIndex[index]+1)
                self.communities[toIndex[index]].append(pointIndex[index]+1)
            tempCommunity = []
            for c in self.communities:
                tempCommunity.append('  '.join([str(i) for i in c]))


        # print('tempPair', tempPair)
        # print('tempDot', tempDot)
        # print('tempCommunity', tempCommunity)

        # 获取原始信息熵
        if not self.isRemovePairs and not self.isRemoveDots and not self.isChangeCommunity:
            self.dots = []
            self.pairs = []
            self.changeSets = []
            self.communities = []
            self.entropy = self.staticEntropy
            self.entropy = self.ig.network.get_entropy()
        else:
            self.entropy = self.ig.network.get_entropy(pair=tempPair, community=tempCommunity, dot=tempDot)
        for i in range(len(self.entropy)):
            self.entropy[i] = float(str(self.entropy[i]).replace('\n', ''))
        print(['社区%d:  %f'%(i+1, self.entropy[i]) for i in range(len(self.entropy))])
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def triggerUpdate(self):
        self.trigger = True

    def draw(self, qp):
        index = 0
        for i in range(len(self.entropy)):
            pen = QPen(QColor(self.ig.colors[i]), 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(5, index * 20 + 20, "●")
            pen = QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(20, index * 20 + 20,
                        '{:<10}{}'.format('社区%d的H(X|Y)值：'%(index + 1), '%.6f'%(self.entropy[i])))
                        # '{:<10}{}'.format('社区%d的信息熵：'%(index + 1), '%.6f'%(self.entropy[i])))
            index += 1
        qp.drawText(20, (index + 1) * 20, '{:<10}{}'.format('H(X|Y)值的总和：', '%.6f'%(sum([i for i in self.entropy]))))
        # qp.drawText(20, (index + 1) * 20, '{:<10}{}'.format('信息熵的总和：', '%.6f'%(sum([i for i in self.entropy]))))
        self.descLabel.setGeometry(20, (index + 2) * 20, 260, 400)
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
            # palette1 = QPalette()
            # # palette1.setColor(self.backgroundRole(), QColor(192,253,123))   # 设置背景颜色
            # palette1.setBrush(b.backgroundRole(), QBrush(QPixmap('a.png')))  # 设置背景图片
            # b.setPalette(palette1)
            # b.setIcon(QIcon("a.png"))
            # b.setIconSize(QSize(25, 25))
            # b.setParent(self)
            self.addWidget(b)
            b.setAttribute(Qt.WA_TranslucentBackground, True)
            b.show()
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
                line.restore(saveColor=True)
                line.setOpacity(.3)

    def leavePoint(self, saveColor=None):
        if saveColor:
            for i in range(len(self.buttons)):
                self.buttons[i].restore(saveColor=saveColor)
            for i in range(len(self.lineItem)):
                self.lineItem[i].restore(saveColor=saveColor)
        else:
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
        vpResultView.isRemoveDots = False
        vpResultView.isRemovePairs = False
        vpResultView.isChangeCommunity = False
        vpResultView.updateEntropy()

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
        # self.show()

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
                pen = qp.pen()
                pen.setColor(QColor(self.ig.points[i].color))
                qp.setPen(pen)
                qp.setRenderHint(QtGui.QPainter.Antialiasing)
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
            message = '布局完成'
            if self.ig.layoutSelection is 'FR':
                message = 'Fruchterman-Reingold布局完成'
            elif self.ig.layoutSelection is 'KK':
                message = 'Kamada-Kawai布局完成'
            messenger.changeStatusBar(message)



class InteractGraph(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.network = None
        self.threadDone = False
        self.layoutSelection = 'FR'
        self.readPoint()
        self.readLine()
        self.initNetwork()
        self.initUI()

    def initNetwork(self):
        self.network = Network()
        self.network.import_network_information()
        self.network.set_community_member()

    def initUI(self):
        self.hide()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("程序主窗口")

        self.file_menu = QMenu('&文件', self)
        self.file_menu.addAction('&打开', self.loadData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        # self.file_menu.addAction('&重新布局', self.reloadLayout,
        #                          QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.file_menu.addAction('&还原', self.restoreData,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_D)
        self.file_menu.addAction('&退出', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.menuBar().addSeparator()
        self.menuBar().addAction('&3D图显示/关闭', self.change3DViewState)
        self.menuBar().addSeparator()
        self.layout_menu = QMenu('&布局选择', self)
        self.layout_menu.addAction('&FR布局', self.reloadFRLayout)
        self.layout_menu.addAction('&KK布局', self.reloadKKLayout)
        self.menuBar().addMenu(self.layout_menu)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&还原', self.restoreData)
        self.menuBar().addSeparator()
        self.menuBar().addAction('&绘制关系图', self.network.drawGraph)
        self.menuBar().addSeparator()

        self.menuBar().addAction('&帮助', self.about)

        self.main_widget = QWidget(self)

        l = QGridLayout(self.main_widget)

        global vLineView
        global vLineScene
        global vpFrontView
        global vpResultView

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
        v3DView = None
        # v3DView = self.get3DView()
        self.v3DView = v3DView
        # v3DView.setAutoBufferSwap(False)
        # v3DView.show()

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
        vpResultView.show()
        QShortcut(QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_F), self, self.searchPoint)
        self.searchState = False

    def getCurrentCursorPos(self):
        return vLineView.mapToScene(self.cursor().pos())

    def get3DView(self, dynamic=None):
        w = gl.GLViewWidget()
        w.opts['distance'] = 10
        w.hide()
        w.setWindowTitle('Network 3D Graph')

        g = gl.GLGridItem()
        w.addItem(g)
        colors = []
        fr = FR3DLayout()
        if dynamic is None:
            points = fr.outputLayout()
        else:
            self.dynamicPoints = fr.outputLayout(dynamic=dynamic)
            points = self.dynamicPoints[0]
        # print(points)
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

        self.scatterPlotPos = pos
        self.scatterPlot = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        self.scatterPlot.translate(5, 5, 0)
        # sp1.scale(10, 10, 10)

        self.linePlot = []
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
            # plt.scale(10, 10, 10)
            w.addItem(plt)
            self.linePlot.append(plt)

        w.addItem(self.scatterPlot)
        self.v3DView = w
        if dynamic:
            # 显示动态过程
            self.dynamicPointsIndex = 0
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update)
            self.timer.start(100)
            print('start timer')
        return w
        # p4.setData(z=z[index % z.shape[0]])

    def update(self):
        if self.dynamicPointsIndex >= len(self.dynamicPoints):
            self.dynamicPointsIndex = 0
        sizes = []
        for i in range(len(self.scatterPlotPos)):
            self.scatterPlotPos[i] = ((self.dynamicPoints[self.dynamicPointsIndex][i+1][0]- 1700)/300.0,
                                      (self.dynamicPoints[self.dynamicPointsIndex][i+1][1]- 1700)/300.0,
                                       (self.dynamicPoints[self.dynamicPointsIndex][i+1][2]- 200)/300.0)
            sizes.append(0.05)
        self.scatterPlot.setData(pos=self.scatterPlotPos)
        self.scatterPlot.setData(size=sizes)

        for i in range(len(self.lines)):
            x = [self.scatterPlotPos[self.lines[i].a-1][0], self.scatterPlotPos[self.lines[i].b-1][0]]
            y = [self.scatterPlotPos[self.lines[i].a-1][1], self.scatterPlotPos[self.lines[i].b-1][1]]
            z = [self.scatterPlotPos[self.lines[i].a-1][2], self.scatterPlotPos[self.lines[i].b-1][2]]
            pts = np.vstack([x, y, z]).transpose()
            self.linePlot[i].setData(pos=pts)

        self.dynamicPointsIndex += 1

    def change3DViewState(self):
        if self.v3DView is None:
            message = '3D视图创建中...'
            messenger.changeStatusBar(message)
            v3DView = self.get3DView(dynamic=True)
            self.v3DView = v3DView
            self.v3DView.show()
            return
            # 不支持在其他线程生成QOpenGLContext
            # try:
            #     _start_new_thread(self.get3DView, (self,))
            # except Exception as e:
            #     print("Error: unable to start thread")
            #     message = '创建3D视图失败！'
            #     messenger.changeStatusBar(message)
            #     print(e)
            # return
        if self.v3DView.isVisible():
            self.v3DView.hide()
            self.timer.stop()
        else:
            self.v3DView.resize(400, 400)
            self.v3DView.show()
            self.timer.start()

    def center(self):  # 主窗口居中显示函数
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.move((screen.width() - APP_WIDTH) / 2, (screen.height() - APP_HEIGHT) / 2)

    def reloadFRLayout(self):
        self.layoutSelection = 'FR'
        self.reloadLayout()

    def reloadKKLayout(self):
        self.layoutSelection = 'KK'
        self.reloadLayout()

    def reloadLayout(self):
        if self.layoutSelection is 'FR':
            message = 'Fruchterman-Reingold重新布局中...'
            messenger.changeStatusBar(message)
            # 创建线程
            try:
                _start_new_thread(self.reloadLayoutThread, (self,))
            except Exception as e:
                print("Error: unable to start thread")
                message = 'Fruchterman-Reingold布局失败！'
                messenger.changeStatusBar(message)
                print(e)
        elif self.layoutSelection is 'KK':
            message = 'Kamada-Kawai重新布局中...'
            messenger.changeStatusBar(message)
            # 创建线程
            try:
                _start_new_thread(self.reloadLayoutThread, (self,))
            except Exception as e:
                print("Error: unable to start thread")
                message = 'Kamada-Kawai布局失败！'
                messenger.changeStatusBar(message)
                print(e)

    def reloadLayoutThread(self, useless):
        if self.layoutSelection is 'FR':
            fr = FRLayout()
            fr.outputLayout()
        elif self.layoutSelection is 'KK':
            kk = KKLayout()
            kk.outputLayout()
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
    Left  Button：拖曳移动节点，点击删除线段
    Mid   Button：点击删除节点
    Right Button：右键选择节点社区
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
        pointsLines = open('points.txt').readlines()
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

    def readLine(self, again=False):
        lineLines = open('lines.txt').readlines()  if os.path.isfile('lines.txt') else []
        length = len(open(NETWORK_FILE).readlines())
        if len(lineLines) != length and not again:
            self.outputLines()
            self.readLine(again=True)
            return
        elif len(lineLines) != length and again:
            print("Error generate lines.txt")
        self.lines = []
        for line in lineLines:
            try:
                a, b, c, d = line.strip().replace('"', '').split()
                d = d[:-2]
                self.lines.append(Line(int(a), int(b), int(c), color=d))
            except Exception as e:
                print(e)

    def outputLines(self):
        # 2 1 1 "#FF0099FF"
        f = open('lines.txt', 'w')
        cs = ["#FF0099FF", "#CC00FFFF", "#3300FFFF", "#0066FFFF", "#00FFFFFF", "#00FF66FF",
              "#33FF00FF", "#CCFF00FF", "#FF9900FF", "#FF0000FF", "#000000FF"]

        lines = open(COMMUNITY_FILE, 'r', encoding='utf-8').readlines()
        communities = [Community() for i in range(len(lines))]
        for i in range(len(lines)):
            line = lines[i]
            _, members_list = line.split(':')
            members = members_list.strip().split(' ')
            for m in members:
                if not m.isdigit():
                    continue
                m = int(m)
                communities[i].vertexes.append(m)

        lineColors = [] # [[a, b, c, color]]
        lines = open(NETWORK_FILE, 'r').readlines()
        for i in range(len(lines)):
            a, b = lines[i].replace('\n', '').split(' ')
            a = int(a)
            b = int(b)
            same_side = False
            for c in communities:
                if a in c.vertexes and b in c.vertexes:
                    same_side = True
                    ci = communities.index(c)
                    lineColors.append([a, b, ci, cs[ci]])
                    break
            if not same_side:
                lineColors.append([a, b, len(cs), cs[-1]])
            f.write(str(lineColors[i][0]) + ' ' + str(lineColors[i][1]) + ' ' + str(lineColors[i][2]) +
                    ' "' + lineColors[i][3] +'"\n')
        f.flush()
        f.close()

    def updateGraph(self):
        pass

    def showData(self):
        print("Points Length: ", len(self.points))
        for p in self.points:
            print("Point:", ' '.join([str(p.name), str(p.x), str(p.y), p.color]))

        print("Lines Length: ", len(self.lines))
        for l in self.lines:
            print("Lines:", ' '.join([str(l.a), str(l.b), str(l.color_index), l.color]))

    def searchPoint(self):
        index, ok = QInputDialog.getText(self, "搜索", "节点编号:", QLineEdit.Normal, "1")
        index = int(index) - 1
        # if index in range(len(vLineScene.buttons)):
        #     vLineScene.focusPoint(index)
        try:
            index = int(index) - 1
            if index in range(len(vLineScene.buttons)):
                vLineScene.focusPoint(index)
        except Exception as e:
            print(e)
            messenger.changeStatusBar('Error ID input.')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ic = IconManager()
    ic.generateIcon()
    ig = InteractGraph()
    ig.setWindowTitle("可视化分析软件")
    # ig.showData()
    ig.show()
    app.exec_()
