# -*- coding: utf-8 -*-
# @Time    : 2018/6/14 15:46:38
# @Author  : SilverMaple
# @Site    : https://github.com/SilverMaple
# @File    : visualization.py
import win32api
import win32con
# import igraph.vendor.texttable
from matplotlib.font_manager import FontProperties
from pylab import *
import subprocess
import os
from igraph import Graph
from xlwt import *
import win_unicode_console
# mpl.rcParams['font.sans-serif'] = ['Times New Roman']
mpl.rcParams['font.sans-serif'] = ['SimHei']

VERTEXES_COUNT = 0
NETWORK_FILE = 'f1.txt'
COMMUNITY_FILE = 'f2.txt'
MUTUAL_INFORMATION_FILE = 'mutualInformation.txt'
C_PLUS_DIR = 'c_plus/release'
CALCULATE_EXE = 'cal_InformationEntropy.exe'
INPUT_EDGE_FILE = C_PLUS_DIR + '/Edge.txt'
INPUT_COMMUNITY_FILE = C_PLUS_DIR + '/Community.txt'
OUTPUT_ENTROPY_FILE = C_PLUS_DIR + '/output_communityEntropy.txt'
OUTPUT_BETWEEN_LINES_FILE = C_PLUS_DIR + '/community_edge.txt'

# COLOR_CONFIG = ["#FF0099FF", "#CC00FFFF", "#3300FFFF", "#0066FFFF", "#00FFFFFF", "#00FF66FF",
#               "#33FF00FF", "#CCFF00FF", "#FF9900FF", "#FF0000FF", "#000000FF"]
COLOR_CONFIG = ["#FF0000FF", "#0066FFFF", "#CC00FFFF", "#33FF00FF", "#FF9900FF",
                "#3300FFFF", "#00FFFFFF", "#006400FF", "#CCFF00FF", "#FF0099FF", "#000000FF"]
SHAPE_CONFIG = ["circle", "triangle-up", "rectangle", "star", "diamond",
                "triangle-down", "darts", "cross", "arrow", "heart", "triangle-down"]


class Community():

    def __init__(self):
        self.vertexes = []
        self.edges = []
        self.color = None
        self.name = None
        self.entropy = 0


class Network():

    def __init__(self):
        self.vertexes = []
        self.edges = []
        self.graph = Graph()
        self.get_vertexes_count()
        self.visual_style = self.init_visual_style()

    def init_visual_style(self):
        self.color_dict = {0: "blue", 1: "green", 2:"red", 3:"yellow", 4:"orange", 5:"pink", 6:"gray",
                           7:"purple", 8:"white", 9:"black", 10:"cyan"}
        self.shape_dict = {0: "circle", 1: "triangle-up", 2:"rectangle", 3:"triangle-down", 4: "circle",
                           5: "triangle-up", 6:"rectangle", 7: "circle", 8: "triangle-up", 9:"rectangle",
                           10:"triangle-down"}
        self.visual_style = {}
        self.visual_style['vertex_size'] = 20
        self.visual_style['vertex_color'] = [self.color_dict[0] for i in range(VERTEXES_COUNT)]
        # rectangle, circle, hidden, triangle_up, triangle_down
        self.visual_style['vertex_shape'] = [self.shape_dict[0] for i in range(VERTEXES_COUNT)]
        self.visual_style['vertex_label'] = []
        self.visual_style['vertex_label_size'] = 20
        self.visual_style['edge_color'] = []
        # self.visual_style['layout'] = self.graph.layout('kamada_kawai')
        self.visual_style['bbox'] = (1000, 1000)
        self.visual_style['margin'] = 20
        return self.visual_style

    def get_vertexes_count(self):
        lines = open(COMMUNITY_FILE, 'r', encoding='utf-8').readlines()
        global VERTEXES_COUNT
        VERTEXES_COUNT = 0
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
        print('{:<30}\t{:<20}'.format('Reading network file: \t', NETWORK_FILE))
        lines = open(NETWORK_FILE, 'r').readlines()
        self.graph.add_vertices(VERTEXES_COUNT)
        self.vertexes = [i+1 for i in range(VERTEXES_COUNT)]
        for line in lines:
            a, b = line.replace('\n', '').split(' ')
            a = int(a)
            b = int(b)
            self.graph.add_edges([(a-1, b-1)])
            self.edges.append((a, b))
        self.graph.vs['name'] = [str(i+1) for i in range(self.graph.vcount())]
        # print('---------')
        # print(self.edges)

    # 从文件中导入社区信息，每一行表示一个社区信息，社区名字与具体成员以英文冒号分隔，成员之间以空格分隔，格式如下所示：
    # 社区1:1 2 4 5 6 7 8 11 12 13 14 17 18 20 22
    # 社区2:3 9 10 15 16 19 21 23 24 25 26 27 28 29 30
    # ...
    def set_community_member(self):
        print('{:<30}\t{:<20}'.format('Reading community file:', COMMUNITY_FILE))
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
                # print(m)
                # 设置顶点颜色形状
                self.visual_style['vertex_color'][m-1] = self.color_dict[i]
                self.visual_style['vertex_shape'][m-1] = self.shape_dict[i]
                self.communities[i].vertexes.append(m)
                self.communities[i].color = self.color_dict[i]
        self.visual_style['vertex_label'] = self.graph.vs['name']

        # 设置社区边颜色，同一社区里的线颜色相同，跨社区的线为黑色
        lines = open(NETWORK_FILE, 'r').readlines()
        self.visual_style['edge_color'] = ['black' for i in range(len(lines))]
        for i in range(len(lines)):
            a, b = lines[i].replace('\n', '').split(' ')
            a = int(a)
            b = int(b)
            same_side = False
            index = self.edges.index((a, b))
            for c in self.communities:
                if a in c.vertexes and b in c.vertexes:
                    same_side = True
                    self.visual_style['edge_color'][index] = c.color
                    break
            if not same_side:
                self.visual_style['edge_color'][index] = 'black'

    def show_result(self):
        # show entropy text
        # plot(self.compute_entropy(None))
        # show community
        self.visual_style['layout'] = self.graph.layout('fruchterman_reingold')
        # self.visual_style['layout'] = self.graph.layout('kamada_kawai')
        print(self.graph)
        plot(self.graph, **(self.visual_style))
        plot(self.graph, 'test.png', **(self.visual_style))
        # plot(self.graph)

    def get_entropy(self, pair=None, community=None, dot=None):
        temp_edge_list = self.edges.copy()
        temp_edge_file = open(INPUT_EDGE_FILE, 'w')
        # decide to rewrite input file or not
        if pair:
            for p in pair:
                # 分别去除每一条社区间的边，重新写入输入文件计算熵
                print('remove ', p)
                if p in temp_edge_list:
                    temp_edge_list.remove(p)
                elif (p[1], p[0]) in temp_edge_list:
                    temp_edge_list.remove((p[1], p[0]))
                else:
                    pass
                    # print('Attempt to remove a line that already removed: ', str(p))
        for edge in temp_edge_list:
            temp_edge_file.write(str(edge[0]) + ' ' + str(edge[1]) + '\n')
        temp_edge_file.flush()
        temp_edge_file.close()
        # print('len:', len(temp_edge_list))
        # print('len:', len(self.edges))
        # print('press Enter if necessary...')

        temp_community_file = open(INPUT_COMMUNITY_FILE, 'w')
        if community:
            # 按照格式重新写入社区划分情况
            temp_community_file.write(str(len(community)))
            for c in community:
                temp_community_file.write('\n' + str(len(' '.join(c.split()).split(' '))) + ' ' + c)
        else:
            temp_community_file.write(str(len(self.communities)))
            for c in self.communities:
                temp_community_file.write('\n' + str(len(c.vertexes)) + ' ' + '  '.join(str(i) for i in c.vertexes))
        temp_community_file.flush()
        temp_community_file.close()

        # 调用exe获取输出结果
        old_wd = os.getcwd()
        os.chdir(C_PLUS_DIR)
        cmd = CALCULATE_EXE
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                print(str(line, encoding='gbk'))
            win32api.keybd_event(108, 0, 0, 0)
            win32api.keybd_event(108, 0, win32con.KEYEVENTF_KEYUP, 0)

        if p.returncode == 0:
            # print('Calculate success.')
            pass
        else:
            print('Calculate failed.')
        os.chdir(old_wd)

        # 读取输出文件社区的熵
        entropy_lines = open(OUTPUT_ENTROPY_FILE, 'r').readlines()
        entropy = []
        for line in entropy_lines:
            a, b = line.split('的')
            if not community:
                entropy.append(b)
            else:
                entropy.append(float(b))

        if not pair and not community:
            # set community's attr entropy base on OUTPUT_FILE
            for i in range(len(self.communities)):
                self.communities[i].entropy = entropy[i]

        return entropy
        # return '社区1（三角形）的信息熵：3.12321\n' \
        #        '社区2（圆形）的信息熵：2.31321\n' \
        #        '信息熵的总和：5.43642'

    def get_between_lines(self):
        between_lines = open(OUTPUT_BETWEEN_LINES_FILE).readlines()
        dot_pairs = []
        current_index = -1
        for line in between_lines:
            if line.startswith('社区'):
                # 示例：社区0与社区1间存在如下边：
                a, b = line.split('与社区')
                a = a[2:]
                b = b[:-8]
                dot_pairs.append([(int(a)+1, int(b)+1)])
                current_index += 1
            elif line[0].isdigit():
                a, b = line.strip().split(' ')
                dot_pairs[current_index].append((int(a), int(b)))
            else:
                pass
        return dot_pairs


    def outputExcel(self):
        wb = Workbook(encoding='utf-8')
        ws = wb.add_sheet('statistic')

        font0 = Font()
        font0.name = 'Times New Roman'
        font0.colour = 'Black'
        font0.bold = True
        style_headline = XFStyle()
        style_headline.font = font0

        style_data = XFStyle()
        style_data.font.bold = False

        font1 = Font()
        font1.name = 'Times New Roman'
        font1.colour_index = 3
        font1.bold = False
        style_add = XFStyle()
        style_add.font = font1

        font2 = Font()
        font2.name = 'Times New Roman'
        font2.colour_index = 2
        font2.bold = False
        style_minus = XFStyle()
        style_minus.font = font2

        self.get_entropy()
        ws.write(0, 0, '社区数', style_headline)
        for i in range(len(self.communities)):
            ws.write(0, 2*i+1, self.communities[i].name, style_headline)
            ws.write(1, 2*i+1, float(self.communities[i].entropy), style_data)
            print(self.communities[i].entropy)
            ws.write(0, 2 * i + 2, '+/-', style_headline)
        ws.write(1, 0, str(len(self.communities)), style_data)
        ws.write(0, 2*(len(self.communities))+1, '总信息熵', style_headline)
        ws.write(1, 2*(len(self.communities))+1, sum([float(i.entropy) for i in self.communities]), style_data)

        dot_pairs = self.get_between_lines()
        current_row = 2
        for pairs in dot_pairs:
            title = '社区' + str(pairs[0][0]) + '~' + str(pairs[0][1])
            temp_edge_list = []
            print(title)
            ws.write(current_row, 0, title, style_headline)
            current_row += 1
            for pair in pairs[1:]:
                entropy = self.get_entropy(pair=[pair])
                sum_entropy = 0
                ws.write(current_row, 0, str(pair), style_headline)
                for i in range(len(entropy)):
                    sum_entropy += float(entropy[i])
                    ws.write(current_row, 2*i + 1, float(entropy[i]), style_data)
                    change = float(entropy[i]) - float(self.communities[i].entropy)
                    if abs(change) < 0.000001:
                        ws.write(current_row, 2 * i + 2, '0', style_data)
                    elif float(entropy[i]) > float(self.communities[i].entropy):
                        ws.write(current_row, 2*i + 2, change, style_add)
                    else:
                        ws.write(current_row, 2 * i + 2, change, style_minus)
                ws.write(current_row, 2*(len(entropy))+1, sum_entropy, style_data)
                current_row += 1

        wb.save('统计.xls')
        pass

    def plotGraph(self, x, y, label, xlabel, ylabel, title, names=None, grid=False, yticks=False):
        plt.clf()
        # plt.rcParams['font.sans-serif'] = ['Times New Roman']
        # plt.rcParams['axes.unicode_minus'] = True
        # font1 = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simsun.ttc')
        plt.plot(x, y, marker='o', mec='r', mfc='w', label=label)
        plt.legend()  # 让图例生效
        if names:
            plt.xticks(x, names, rotation=45)
        plt.margins(0)
        plt.subplots_adjust(bottom=0.15)
        plt.xlabel(xlabel)  # X轴标签
        # plt.xlabel(xlabel, fontproperties=my_font)  # X轴标签
        plt.ylabel(ylabel)  # Y轴标签
        plt.xticks(range(min(x), max(x)+1))
        if yticks:
            plt.yticks(np.linspace(min(y), max(y), num=10))
        if grid:
            plt.grid()
        tmp_x = abs(max(x)-min(x))*0.1
        tmp_y = abs(max(y)-min(y))*0.2
        plt.xlim((min(x)-tmp_x, max(x)+tmp_x))
        plt.ylim((min(y)-tmp_y, max(y)+tmp_y))
        plt.title(title)  # 标题
        plt.show()

    def drawGraphDeprecated(self):
        lines = open(MUTUAL_INFORMATION_FILE, 'r').readlines()
        index = -1
        mutualInformation = []
        totalEntropy = []
        communityCluster = []
        for line in lines:
            if not index < 10:
                communityCluster.remove([])
                break
            if line.startswith("Q值为："):
                index += 1
                i = line.strip()[4:]
                mutualInformation.append(i)
                communityCluster.append([])
            elif '中的结点有：' in line:
                communityCluster[index].append(line.strip().split('：')[1])
            else:
                pass

        print('communityCluster: ', communityCluster)

        for c in communityCluster:
            totalEntropy.append(sum(self.get_entropy(community=c)))

        print('mutualInformation: ', mutualInformation)
        print('totalEntropy', totalEntropy)

        dataSetName = u'Dolphin'
        self.plotGraph(range(2, len(totalEntropy)+2), totalEntropy, u'平均互信息最大时',
                       u'社区个数', u'总信息熵', title=dataSetName+u'数据集社区个数-总信息熵关系折线图')

        self.plotGraph(range(2, len(mutualInformation)+1), list(map(float, mutualInformation[1:])), u'GN算法进行社区划分',
                       u'社区个数', u'平均互信息', title=dataSetName+u'数据集社区个数-平均互信息关系折线图')

        self.plotGraph(mutualInformation[1:], totalEntropy, u'GN算法进行社区划分',
                       u'平均互信息', u'总信息熵', title=dataSetName + u'数据集平均互信息-总信息熵关系折线图')

        self.plotGraph(range(2, len(totalEntropy)+2),
                       [float(mutualInformation[i+1])*totalEntropy[i] for i in range(len(totalEntropy))],
                       u'GN算法进行社区划分', u'社区个数', u'平均互信息与总信息熵乘积',
                       title=dataSetName + u'数据集社区个数-平均互信息与总信息熵乘积关系折线图')

        self.plotGraph(range(2, len(totalEntropy)+2),
                       [float(mutualInformation[i+1]) / totalEntropy[i] for i in range(len(totalEntropy))],
                       u'GN算法进行社区划分', u'社区个数', u'平均互信息与总信息熵比例',
                       title=dataSetName + u'数据集社区个数-平均互信息与总信息熵比例关系折线图')

        print([ '~'.join([str(i), str(i+1)]) for i in range(2, len(totalEntropy))])
        self.plotGraph([ '~'.join([str(i), str(i+1)]) for i in range(2, len(totalEntropy))],
                       [(float(mutualInformation[i+1])-float(mutualInformation[i])) / (totalEntropy[i]-totalEntropy[i-1]) for i in range(1, len(totalEntropy)-1)],
                       u'GN算法进行社区划分', u'社区个数', u'平均互信息与总信息熵比例',
                       title=dataSetName + u'数据集社区个数-平均互信息与总信息熵变化比例关系折线图')

    def drawGraph(self):
        lines = open(MUTUAL_INFORMATION_FILE, 'r').readlines()
        index = -1
        mutualInformation = []
        totalEntropy = []
        communityCluster = []
        for line in lines:
            if not index < 10:
                communityCluster.remove([])
                break
            if line.startswith("Q值为："):
                index += 1
                i = line.strip()[4:]
                mutualInformation.append(i)
                communityCluster.append([])
            elif '中的结点有：' in line:
                communityCluster[index].append(line.strip().split('：')[1])
            else:
                pass

        # print('communityCluster: ', communityCluster)

        for c in communityCluster:
            totalEntropy.append(sum(self.get_entropy(community=c)))

        # print('mutualInformation: ', mutualInformation)
        # print('totalEntropy', totalEntropy)
        # print(range(2, len(mutualInformation)+1))
        # print(mutualInformation[1:])

        dataSetName = u'Dolphin'
        self.plotGraph(range(2, len(mutualInformation)+1), list(map(float, mutualInformation[1:])), u'AMI-GN算法',
                       u'社区个数', u'平均互信息值', title="")
                       # u'社区个数', u'平均互信息(Ip)值', title="")
        self.plotGraph(range(2, len(mutualInformation) + 1), list(map(float, mutualInformation[1:])), u'AMI-GN算法',
                       u'社区个数', u'平均互信息值', title="", grid=True)
        self.plotGraph(range(2, len(mutualInformation) + 1), list(map(float, mutualInformation[1:])), u'AMI-GN算法',
                       u'社区个数', u'平均互信息值', title="", grid=False, yticks=True)
        self.plotGraph(range(2, len(mutualInformation) + 1), list(map(float, mutualInformation[1:])), u'AMI-GN算法',
                       u'社区个数', u'平均互信息值', title="", grid=True, yticks=True)


if __name__ == '__main__':
    win_unicode_console.enable()
    print('Reading file....')
    n = Network()
    n.import_network_information()
    n.set_community_member()
    n.show_result()
    n.outputExcel()
    n.drawGraph()