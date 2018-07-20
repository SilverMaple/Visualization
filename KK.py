# -*- coding: utf-8 -*-
# @Time    : 2018/7/20 10:00
# @Author  : SilverMaple
# @Site    : https:#github.com/SilverMaple
# @File    : KK.py

import math
import random
import traceback

import numpy
import win_unicode_console
from numpy.random.mtrand import rand, randint

from FR import Community

VERTEXES_COUNT = 0
NETWORK_FILE = 'f1.txt'
COMMUNITY_FILE = 'f2.txt'

paper1 = "Tomihisa Kamada and Satoru Kawai: An algorithm for drawing general " \
        "indirect graphs. Information Processing Letters 31(1):7-15, 1989"
paper2 = "Tomihisa Kamada: On visualization of abstract objects and relations. " \
         "Ph.D. dissertation, Dept. of Information Science, Univ. of Tokyo, Dec. 1988."

# Kamada-Kawai algorithm
class KKLayout:
    # Creates an instance for the specified graph and distance metric.
    def __init__(self):
        self.graph = None
        self.vertexes = []
        self.edges = []
        self.setAttribute(iterations=500, epsilon=0.1, k=1, l=0.9)
        self.get_vertexes_count()

    def setAttribute(self, iterations, epsilon, k, l):
        self.EPSILON = epsilon # 0.1
        self.currentIteration = None
        self.maxIterations = iterations  # 2000
        self.status = "KKLayout"
        self.L = None  # 弹簧长度系数，即边的理想长度
        self.K = k # 1  # 弹簧强度系数，对算法结果影响不大
        self.dm = []  # 最短距离矩阵，使用Dijkstra最短路径算法
        self.isAdjustForGravity = True
        self.isExchangeVertices = True
        self.vertices = []
        self.positions = []
        self.PLOT_WIDTH = 500
        self.PLOT_HEIGHT = 500
        self.size = {'width': self.PLOT_WIDTH, 'height': self.PLOT_HEIGHT}

        # Retrieves graph distances between vertices of the visible graph
        self.distance = []

        # The diameter of the visible graph.In other words, the maximum over all pairs
        # of vertices of the length of the shortest path between a and b of the visible graph.
        # 图直径
        self.diameter = 5.0  # 5.0

        # A multiplicative factor which partly specifies the "preferred" length of an edge (L).
        self.length_factor = l # 0.9

        # A multiplicative factor which specifies the fraction of the graph's diameter to be
        # used as the inter-vertex distance between disconnected vertices.
        self.disconnected_multiplier = 0.7  # 0.5

        self.locations = []
        self.minEnergy = None
        self.minIndex = -1
        self.finalPos = None

    def get_vertexes_count(self):
        global VERTEXES_COUNT
        VERTEXES_COUNT *= 0
        lines = open(COMMUNITY_FILE, 'r', encoding='utf-8').readlines()
        for i in range(len(lines)):
            # global  VERTEXES_COUNT
            line = lines[i]
            name, members_list = line.split(':')
            VERTEXES_COUNT += len(members_list.split())

    def setSize(self, width, height):
        self.size = {'width': width, 'height': height}

    # Returns True once the current iteration has passed the maximum count.
    def done(self):
        if self.currentIteration > self.maxIterations:
            return True
        return False

    def initialize(self):
        # 1
        # for i in range(11):
        #     connections = []
        #     RandCx1 = randint(0, 2)
        #     for j in range(RandCx1+1):
        #         RandCx2 = rand(0, 10)
        #         if RandCx2 != j:
        #             connections.append(RandCx2)
        #     nodes.append({'idx': i, "conn": connections})
        self.graph = []
        for i in range(len(self.vertexes)):
            connections = []
            for j in range(len(self.edges)):
                if i+1 in self.edges[j]:
                    if i+1 == self.edges[j][0]:
                        connections.append(self.edges[j][1]-1)
                    else:
                        connections.append(self.edges[j][0]-1)
            self.graph.append({'idx': i, "conn": connections})
        # 2
        self.currentIteration = 0
        if self.graph != None and self.size != None:
            height = self.size['height']
            width = self.size['width']
            n = len(self.graph)
            # self.dm = [] # new Array[n][n]
            self.dm = numpy.zeros((n, n))
            self.vertices = self.graph
            self.positions = []
            # assign IDs to all visible vertices
            loopTimes = 1
            # while True:
            for i in range(loopTimes):
                try:
                    index = 0
                    for v in self.graph:
                        xyd = self.transform()
                        self.vertices[index] = v
                        self.positions.append(xyd)
                        index += 1
                    break
                except Exception as e:
                    print(e)
            # self.diameter = 5.0 # DistanceStatistics. < V, E > diameter(graph, distance, True)
            L0 = min(height, width)
            self.L = (L0 / self.diameter) * self.length_factor # length_factor used to be hardcoded to 0.9
            # L = 0.75 * sqrt(height * width / n)
            for i in range(n-1):
                for j in range(i+1, n):
                    d_ij = self.getDistance(self.vertices[i], self.vertices[j])
                    d_ji = self.getDistance(self.vertices[j], self.vertices[i])
                    dist = self.diameter * self.disconnected_multiplier
                    if d_ij != None:
                        dist = min(d_ij, dist)
                    if d_ji != None:
                        dist = min(d_ji, dist)
                    self.dm[i][j] = dist
                    self.dm[j][i] = dist

    # init node 's position
    # @return ArrayObject
    def transform(self):
        # x = randint(10, self.size['width'] - 1)
        # y = randint(10, self.size['height'] - 1)
        x = random.uniform(10, self.PLOT_WIDTH)
        y = random.uniform(10, self.PLOT_HEIGHT)
        return {'x': x, 'y': y}

    # For now, it is just a very simple strategy to get weight of distance
    # TODO: fix it!
    # @ param from
    # @ param to
    # @return distance weight
    def getDistance(self, v1, v2):
        fromid = v1['idx']
        toid = v2['idx']
        if toid in v1['conn']:
            weight = 1
        else:
            weight = None
        return weight

    def step(self):
        try:
            self.currentIteration += 1
            energy = self.calcEnergy()
            if self.minEnergy:
                if energy < self.minEnergy:
                    self.minEnergy = energy
                    self.minIndex = self.currentIteration
                    self.finalPos = self.positions
            else:
                self.minEnergy = energy
                self.finalPos = self.positions
            self.status = "Kamada-Kawai V=" + str(len(self.graph)) + "(" + str(len(self.graph)) \
                          + ")" + " IT: " + str(self.currentIteration) + " E=" + str(energy)
            print(self.status)

            n = len(self.graph)
            if n == 0:
                return
            maxDeltaM = 0
            pm = -1 # the node having max deltaM
            for i in range(n):
                deltam = self.calcDeltaM(i)
                if maxDeltaM < deltam:
                    maxDeltaM = deltam
                    pm = i
            if pm == -1:
                return

            # 找到偏移量最大的点下标，进行迭代偏移直至偏移量小于阈值
            for i in range(100):
                dxy = self.calcDeltaXY(pm)
                self.positions[pm]['x'] = self.positions[pm]['x'] + dxy[0]
                self.positions[pm]['y'] = self.positions[pm]['y'] + dxy[1]
                deltam = self.calcDeltaM(pm)
                if deltam < self.EPSILON:
                    break

            # 调整网络坐标
            if self.isAdjustForGravity:
                self.adjustForGravity()

            if self.isExchangeVertices and maxDeltaM < self.EPSILON:
                energy = self.calcEnergy()

                for i in range(n-1):
                    for j in range(i+1, n):
                        xenergy = self.calcEnergyIfExchanged(i, j)
                        if energy > xenergy:
                            sx = self.positions[i]['x']
                            sy = self.positions[i]['y']
                            self.positions[i]['x'] = self.positions[j]['x'] #.setLocation(xydata[j])
                            self.positions[i]['y'] = self.positions[j]['y']
                            self.positions[j]['x'] = sx
                            self.positions[j]['x'] = sy
                            return
        except Exception as e:
            traceback.print_exc()
            print(e)

    # Shift all vertices so that the center of gravity is located at
    # the center of the screen.
    def adjustForGravity(self):
        d = self.size
        height = d['height']
        width = d['width']
        gx = 0
        gy = 0
        cnt = len(self.positions)
        for i in range(cnt):
            gx += self.positions[i]['x']
            gy += self.positions[i]['y']
        gx /= cnt
        gy /= cnt
        diffx = width / 2 - gx
        diffy = height / 2 - gy
        for i in range(cnt):
            self.positions[i]['x'] = self.positions[i]['x'] + diffx
            self.positions[i]['y'] = self.positions[i]['y'] + diffy


    # Determines a step to new position of the vertex m.
    def calcDeltaXY(self, m):
        dE_dxm = 0 # E对x偏微分
        dE_dym = 0 # E对y偏微分
        d2E_d2xm = 0
        d2E_dxmdym = 0
        d2E_dymdxm = 0
        d2E_d2ym = 0
        for i in range(len(self.vertices)):
            if i != m:
                dist = self.dm[m][i]
                l_mi = self.L * dist
                k_mi = self.K / (dist * dist)
                dx = self.positions[m]['x'] - self.positions[i]['x']
                dy = self.positions[m]['y'] - self.positions[i]['y']
                d = math.sqrt(dx * dx + dy * dy)
                ddd = d * d * d
                dE_dxm += k_mi * (1 - l_mi / d) * dx
                dE_dym += k_mi * (1 - l_mi / d) * dy
                d2E_d2xm += k_mi * (1 - l_mi * dy * dy / ddd)
                d2E_dxmdym += k_mi * l_mi * dx * dy / ddd
                d2E_d2ym += k_mi * (1 - l_mi * dx * dx / ddd)

        # d2E_dymdxm equals to d2E_dxmdym.
        d2E_dymdxm = d2E_dxmdym
        denomi = d2E_d2xm * d2E_d2ym - d2E_dxmdym * d2E_dymdxm
        deltaX = (d2E_dxmdym * dE_dym - d2E_d2ym * dE_dxm) / denomi
        deltaY = (d2E_dymdxm * dE_dxm - d2E_d2xm * dE_dym) / denomi
        return [deltaX, deltaY]

    # Calculates the gradient of energy function at the vertex m.
    def calcDeltaM(self, m):
        dEdxm = 0
        dEdym = 0
        for i in range(len(self.vertices)):
            if i != m:
                dist = self.dm[m][i]
                l_mi = self.L * dist
                k_mi = self.K / (dist * dist)
                dx = self.positions[m]['x'] - self.positions[i]['x']
                dy = self.positions[m]['y'] - self.positions[i]['y']
                d = math.sqrt(dx * dx + dy * dy)
                common = k_mi * (1 - l_mi / d)
                dEdxm += common * dx
                dEdym += common * dy
        return math.sqrt(dEdxm * dEdxm + dEdym * dEdym)

    # Calculates the energy function E.
    def calcEnergy(self):
        energy = 0
        for i in range(len(self.vertices)- 1):
            for j in range(i+1, len(self.vertices)):
                dist = self.dm[i][j] # i，j两个节点的图距离
                l_ij = self.L * dist # i，j两个节点的理想距离等于图距离与常数乘积
                k_ij = self.K / (dist * dist) # i，j两点之间的力强度
                dx = self.positions[i]['x'] - self.positions[j]['x']
                dy = self.positions[i]['y'] - self.positions[j]['y']
                d = math.sqrt(dx * dx + dy * dy) # 坐标距离
                energy += k_ij / 2 * (dx * dx + dy * dy + l_ij * l_ij - 2 * l_ij * d)
        return energy

    # Calculates the energy function E as if positions of the
    # specified vertices are exchanged.
    def calcEnergyIfExchanged(self, p, q):
        if p >= q:
            raise Exception("p should be < q")
        energy = 0 # < 0
        for i in range(len(self.vertices) - 1):
            for j in range(i+1, len(self.vertices)):
                ii = i
                jj = j
                if i == p:
                    ii = q
                if j == q:
                    jj = p
                dist = self.dm[i][j]
                l_ij = self.L * dist
                k_ij = self.K / (dist * dist)
                dx = self.positions[ii]['x'] - self.positions[jj]['x']
                dy = self.positions[ii]['y'] - self.positions[jj]['y']
                d = math.sqrt(dx * dx + dy * dy)

                energy += k_ij / 2 * (dx * dx + dy * dy + l_ij * l_ij - 2 * l_ij * d)
        return energy

    def reset(self):
        self.currentIteration = 0

    # 从文件中导入关系图，每一行表示两个节点之间的一条连接，格式如下所示：
    # 2 1
    # 3 1
    # 3 2
    # 4 1
    # ...
    def import_network_information(self):
        lines = open(NETWORK_FILE, 'r').readlines()
        self.vertexes = [i+1 for i in range(VERTEXES_COUNT)]
        for line in lines:
            a, b = line.replace('\n', '').split(' ')
            a = int(a)
            b = int(b)
            self.edges.append((a, b))

    # 从文件中导入社区信息，每一行表示一个社区信息，社区名字与具体成员以英文冒号分隔，成员之间以空格分隔，格式如下所示：
    # 社区1:1 2 4 5 6 7 8 11 12 13 14 17 18 20 22
    # 社区2:3 9 10 15 16 19 21 23 24 25 26 27 28 29 30
    # ...
    def set_community_member(self):
        lines = open(COMMUNITY_FILE, 'r', encoding='utf-8').readlines()
        self.communities = [Community() for i in range(len(lines))]
        for i in range(len(lines)):
            line = lines[i]
            name, members_list = line.split(':')
            self.communities[i].name = name
            members = members_list.strip().split(' ')
            for m in members:
                if not m.isdigit():
                    continue
                m = int(m)
                # 设置顶点颜色形状
                self.communities[i].vertexes.append(m)

    def normalizeScope(self):
        margin = 30
        minx = min(self.positions[i][0] for i in self.positions)
        miny = min(self.positions[i][1] for i in self.positions)
        maxx = max(self.positions[i][0] for i in self.positions)
        maxy = max(self.positions[i][1] for i in self.positions)
        factorx = self.PLOT_WIDTH / (maxx - minx)
        factory = self.PLOT_HEIGHT / (maxy- miny)
        for i in self.positions:
            self.positions[i][0] = (self.positions[i][0] - minx) * factorx
            self.positions[i][1] = (self.positions[i][1] - miny) * factory
        minx = min(self.positions[i][0] for i in self.positions)
        miny = min(self.positions[i][1] for i in self.positions)
        maxx = max(self.positions[i][0] for i in self.positions)
        maxy = max(self.positions[i][1] for i in self.positions)
        fitnessX = (self.PLOT_WIDTH - 2*margin) / (maxx + (self.PLOT_WIDTH - (maxx-minx))/2)
        fitnessY = (self.PLOT_HEIGHT - 2*margin) / (maxy + (self.PLOT_HEIGHT - (maxy-miny))/2)
        print(fitnessX, fitnessY)
        for i in self.positions:
            self.positions[i][0] = (self.positions[i][0] + (self.PLOT_WIDTH - (maxx-minx))/2) * fitnessX + margin
            self.positions[i][1] = (self.positions[i][1] + (self.PLOT_HEIGHT - (maxy-miny))/2) * fitnessY + margin

    def outputPoints(self):
        # "228.918895098647" "319.544170947533" "#FF0000FF"
        f = open('../R_script/points.txt', 'w')
        cs = ['#FF0099FF', '#CC00FFFF', '#3300FFFF']
        # 转化格式
        self.positionsIndex = {i: (self.finalPos[i-1]['x'], self.finalPos[i-1]['y'])
                               for i in range(1, len(self.finalPos)+1)}
        for i in range(len(self.positionsIndex)):
            color = None
            for ci in range(len(self.communities)):
                if i+1 in self.communities[ci].vertexes:
                    try:
                        color = cs[ci]
                    except Exception as e:
                        print(i)
                        print(e)
                    break
            if color is None:
                print(i)
                color = '#FFFFFFFF'

            f.write('"' + str(self.positionsIndex[i+1][0]*0.95) + '" "' + str(self.positionsIndex[i+1][1]*0.95) + '" "' + color +'"\n')
        f.flush()
        f.close()

    def outputLayout(self):
        win_unicode_console.enable()
        print('Reading file....')
        self.setAttribute(iterations=500, epsilon=0.1, k=1, l=0.9)
        self.import_network_information()
        self.set_community_member()
        self.runKK()
        # self.normalizeScope()
        self.outputPoints()
        print(self.minEnergy, self.minIndex)
        print(self.finalPos)

    def runKK(self):
        self.initialize()
        while not self.done():
            self.step()
        print(self.minEnergy, self.minIndex)

if __name__ == '__main__':
    nodes = []

    # Create 11 random nodes
    # for i in range(11):
    #     connections = []
    #     RandCx1 = randint(0, 2)
    #     for j in range(RandCx1+1):
    #         RandCx2 = rand(0, 10)
    #         if RandCx2 != j:
    #             connections.append(RandCx2)
    #     nodes.append({'idx': i, "conn": connections})
    # kklayout = KKLayout(nodes)
    # kklayout.runKK()
    kklayout = KKLayout()
    kklayout.outputLayout()



