# -*- coding: utf-8 -*-
# @Time    : 2018/7/18 11:01
# @Author  : SilverMaple
# @Site    : https://github.com/SilverMaple
# @File    : FR.py

import igraph.vendor.texttable
from pylab import *
import random
from igraph import *
import win_unicode_console

mpl.rcParams['font.sans-serif'] = ['SimHei']


VERTEXES_COUNT = 0
NETWORK_FILE = 'f1.txt'
COMMUNITY_FILE = 'f2.txt'


class Community():

    def __init__(self):
        self.vertexes = []
        self.edges = []
        self.color = None
        self.name = None
        self.entropy = 0


class FRLayout():

    def __init__(self):
        self.vertexes = []
        self.edges = []
        self.get_vertexes_count()

    def setAttribute(self, iterations, attractive_force, repulsive_force, temperature, speed):
        self.iterations = iterations
        self.attractive_force = attractive_force
        self.repulsive_force = repulsive_force
        self.positions = {}
        self.forces = {}
        self.temperature = temperature
        self.PLOT_WIDTH = 500
        self.PLOT_HEIGHT = 500
        self.plot = None
        self.created = False
        self.speed = speed

    def calculate_attraction_force(self, value):
        return value ** 2 / self.attractive_force

    def calculate_repulsion_force(self, value):
        return self.repulsive_force ** 2 / value

    def init_vertices(self):
        # Initialization of vertices positions in random places
        plot_x = self.PLOT_WIDTH
        plot_y = self.PLOT_HEIGHT
        to_ret = []
        for i in range(0, len(self.vertexes)):
            to_ret.append((self.vertexes[i], [random.uniform(0, plot_x),
                                              random.uniform(0, plot_y)]))
        self.positions = dict(to_ret)

    def cool(self):
        # 常数介于0.6~0.95
        return self.temperature * 0.95

    def norm(self, x):
        return math.sqrt(sum(i ** 2 for i in x))

    def sum(self, v1, v2):
        return [x + y for (x, y) in zip(v1, v2)]

    def sub(self, v1, v2):
        return [x - y for (x, y) in zip(v1, v2)]

    def mult(self, v1, scalar):
        return [x * scalar for x in v1]

    def div(self, v1, scalar):
        return [x / scalar for x in v1]

    def algorithm_step(self):
        # Initialization of forces
        for i in range(0, len(self.vertexes)):
            f_node = [0.0, 0.0]
            self.forces[self.vertexes[i]] = f_node
        # Calculation repulsion forces
        for i in range(len(self.vertexes)):
            vertex_1 = self.vertexes[i]
            # for j in range(len(self.vertexes)):
            #     if i == j:
            #         continue
            for j in range(i + 1, len(self.vertexes)):
                vertex_2 = self.vertexes[j]
                delta = self.sub(self.positions[vertex_1], self.positions[vertex_2])
                mod_delta = max(self.norm(delta), 0.02)
                self.forces[vertex_1] = self.sum(self.forces[vertex_1],
                                                 self.mult(self.div(delta, mod_delta),
                                                           self.calculate_repulsion_force(mod_delta))
                                                 )
                self.forces[vertex_2] = self.sub(self.forces[vertex_2],
                                                 self.mult(self.div(delta, mod_delta),
                                                           self.calculate_repulsion_force(mod_delta))
                                                 )
        # Calculation attraction forces
        for edge in self.edges:
            delta = self.sub(self.positions[edge[0]], self.positions[edge[1]])
            mod_delta = max(self.norm(delta), 0.02)
            self.forces[edge[0]] = self.sub(self.forces[edge[0]],
                                            self.mult(self.div(delta, mod_delta),
                                                      self.calculate_attraction_force(mod_delta))
                                            )
            self.forces[edge[1]] = self.sum(self.forces[edge[1]],
                                            self.mult(self.div(delta, mod_delta),
                                                      self.calculate_attraction_force(mod_delta))
                                            )
        # Update positions
        for vertex in self.vertexes:
            disp = self.forces[vertex]
            mod_disp = max(self.norm(disp), 0.02)
            self.positions[vertex] = self.sum(self.positions[vertex], self.mult(
                self.div(disp, mod_disp), min(mod_disp, self.temperature))
                                              )
        # Cool
        self.temperature = self.cool()
        # print(self.temperature)

    def runFR(self):
        self.init_vertices()
        for i in range(0, self.iterations):
            print('FR:', i)
            if self.temperature < 0.02:
                break
            self.algorithm_step()

    def get_vertexes_count(self):
        global VERTEXES_COUNT
        VERTEXES_COUNT *= 0
        lines = open(COMMUNITY_FILE, 'r', encoding='utf-8').readlines()
        for i in range(len(lines)):
            # global  VERTEXES_COUNT
            line = lines[i]
            name, members_list = line.split(':')
            VERTEXES_COUNT += len(members_list.split())

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
        for i in range(len(self.positions)):
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

            f.write('"' + str(self.positions[i+1][0]) + '" "' + str(self.positions[i+1][1]) + '" "' + color +'"\n')
        f.flush()
        f.close()

    def outputLayout(self):
        win_unicode_console.enable()
        print('Reading file....')
        self.setAttribute(100, 2000, 30, 100, 100)
        # n = Network(iterations=100, attractive_force=2000, repulsive_force=30,
        #             temperature=100, speed=10)
        self.import_network_information()
        self.set_community_member()
        self.runFR()
        self.normalizeScope()
        self.outputPoints()


class FR3DLayout():

    def __init__(self):
        self.vertexes = []
        self.edges = []
        self.get_vertexes_count()

    def setAttribute(self, iterations, attractive_force, repulsive_force, temperature, speed):
        self.iterations = iterations
        self.attractive_force = attractive_force
        self.repulsive_force = repulsive_force
        self.positions = {}
        self.forces = {}
        self.temperature = temperature
        self.PLOT_WIDTH = 500
        self.PLOT_HEIGHT = 500
        self.PLOT_DEPTH = 500
        self.plot = None
        self.created = False
        self.speed = speed

    def calculate_attraction_force(self, value):
        return value ** 2 / self.attractive_force

    def calculate_repulsion_force(self, value):
        return self.repulsive_force ** 2 / value

    def init_vertices(self):
        # Initialization of vertices positions in random places
        plot_x = self.PLOT_WIDTH
        plot_y = self.PLOT_HEIGHT
        plot_z = self.PLOT_DEPTH
        to_ret = []
        for i in range(0, len(self.vertexes)):
            to_ret.append((self.vertexes[i], [random.uniform(0, plot_x),
                                              random.uniform(0, plot_y),
                                              random.uniform(0, plot_z)]))
        self.positions = dict(to_ret)

    def cool(self):
        # 常数介于0.6~0.95
        return self.temperature * 0.95

    def norm(self, x):
        return math.sqrt(sum(i ** 2 for i in x))

    def sum(self, v1, v2):
        return [x + y for (x, y) in zip(v1, v2)]

    def sub(self, v1, v2):
        return [x - y for (x, y) in zip(v1, v2)]

    def mult(self, v1, scalar):
        return [x * scalar for x in v1]

    def div(self, v1, scalar):
        return [x / scalar for x in v1]

    def algorithm_step(self):
        # Initialization of forces
        for i in range(0, len(self.vertexes)):
            f_node = [0.0, 0.0, 0.0]
            self.forces[self.vertexes[i]] = f_node
        # Calculation repulsion forces
        for i in range(len(self.vertexes)):
            vertex_1 = self.vertexes[i]
            # for j in range(len(self.vertexes)):
            #     if i == j:
            #         continue
            for j in range(i + 1, len(self.vertexes)):
                vertex_2 = self.vertexes[j]
                delta = self.sub(self.positions[vertex_1], self.positions[vertex_2])
                mod_delta = max(self.norm(delta), 0.02)
                self.forces[vertex_1] = self.sum(self.forces[vertex_1],
                                                 self.mult(self.div(delta, mod_delta),
                                                           self.calculate_repulsion_force(mod_delta))
                                                 )
                self.forces[vertex_2] = self.sub(self.forces[vertex_2],
                                                 self.mult(self.div(delta, mod_delta),
                                                           self.calculate_repulsion_force(mod_delta))
                                                 )
        # Calculation attraction forces
        for edge in self.edges:
            delta = self.sub(self.positions[edge[0]], self.positions[edge[1]])
            mod_delta = max(self.norm(delta), 0.02)
            self.forces[edge[0]] = self.sub(self.forces[edge[0]],
                                            self.mult(self.div(delta, mod_delta),
                                                      self.calculate_attraction_force(mod_delta))
                                            )
            self.forces[edge[1]] = self.sum(self.forces[edge[1]],
                                            self.mult(self.div(delta, mod_delta),
                                                      self.calculate_attraction_force(mod_delta))
                                            )
        # Update positions
        for vertex in self.vertexes:
            disp = self.forces[vertex]
            mod_disp = max(self.norm(disp), 0.02)
            self.positions[vertex] = self.sum(self.positions[vertex], self.mult(
                self.div(disp, mod_disp), min(mod_disp, self.temperature))
                                              )
        # Cool
        self.temperature = self.cool()
        # print(self.temperature)

    def runFR(self):
        self.init_vertices()
        for i in range(0, self.iterations):
            print('FR:', i)
            if self.temperature < 0.02:
                break
            self.algorithm_step()

    def get_vertexes_count(self):
        global VERTEXES_COUNT
        VERTEXES_COUNT *= 0
        lines = open(COMMUNITY_FILE, 'r', encoding='utf-8').readlines()
        for i in range(len(lines)):
            # global  VERTEXES_COUNT
            line = lines[i]
            name, members_list = line.split(':')
            VERTEXES_COUNT += len(members_list.split())

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
        minz = min(self.positions[i][2] for i in self.positions)

        maxx = max(self.positions[i][0] for i in self.positions)
        maxy = max(self.positions[i][1] for i in self.positions)
        maxz = max(self.positions[i][2] for i in self.positions)
        factorx = self.PLOT_WIDTH / (maxx - minx)
        factory = self.PLOT_HEIGHT / (maxy- miny)
        factorz = self.PLOT_DEPTH / (maxz- minz)

        for i in self.positions:
            self.positions[i][0] = (self.positions[i][0] - minx) * factorx
            self.positions[i][1] = (self.positions[i][1] - miny) * factory
            self.positions[i][2] = (self.positions[i][2] - minz) * factorz
        minx = min(self.positions[i][0] for i in self.positions)
        miny = min(self.positions[i][1] for i in self.positions)
        minz = min(self.positions[i][2] for i in self.positions)
        maxx = max(self.positions[i][0] for i in self.positions)
        maxy = max(self.positions[i][1] for i in self.positions)
        maxz = max(self.positions[i][2] for i in self.positions)
        fitnessX = (self.PLOT_WIDTH - 2*margin) / (maxx + (self.PLOT_WIDTH - (maxx-minx))/2)
        fitnessY = (self.PLOT_HEIGHT - 2*margin) / (maxy + (self.PLOT_HEIGHT - (maxy-miny))/2)
        fitnessZ = (self.PLOT_DEPTH - 2*margin) / (maxz + (self.PLOT_DEPTH - (maxz-minz))/2)
        print(fitnessX, fitnessY, fitnessZ)
        for i in self.positions:
            self.positions[i][0] = (self.positions[i][0] + (self.PLOT_WIDTH - (maxx-minx))/2) * fitnessX + margin
            self.positions[i][1] = (self.positions[i][1] + (self.PLOT_HEIGHT - (maxy-miny))/2) * fitnessY + margin
            self.positions[i][2] = (self.positions[i][2] + (self.PLOT_DEPTH - (maxz-minz))/2) * fitnessZ + margin

    def outputPoints(self):
        # "228.918895098647" "319.544170947533" "#FF0000FF"
        # f = open('../R_script/points.txt', 'w')
        # cs = ['#FF0099FF', '#CC00FFFF', '#3300FFFF']
        return self.positions

    def outputLayout(self):
        win_unicode_console.enable()
        print('Reading file....')
        self.setAttribute(100, 2000, 30, 100, 100)
        # n = Network(iterations=100, attractive_force=2000, repulsive_force=30,
        #             temperature=100, speed=10)
        self.import_network_information()
        self.set_community_member()
        self.runFR()
        self.normalizeScope()
        return self.outputPoints()

if __name__ == '__main__':
    win_unicode_console.enable()
    print('Reading file....')
    n = FRLayout()
    n.setAttribute(100, 2000, 30, 100, 100)
    # n = Network(iterations=100, attractive_force=2000, repulsive_force=30,
    #             temperature=100, speed=10)
    n.import_network_information()
    n.set_community_member()
    n.runFR()
    n.normalizeScope()
    n.outputPoints()
