# # -*- coding: utf-8 -*-
# # @Time    : 2019/3/7 19:11
# # @Author  : SilverMaple
# # @Site    : https://github.com/SilverMaple
# # @File    : algorithmView.py
#
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy as np
from copy import deepcopy

# epochs = 34
# n = 7
# outer_radius = .3
# inner_radius = outer_radius * 2 * np.pi / n
# theta = np.linspace(0, 2 * np.pi, n + 1)[:-1]
# length = np.random.rand(n)


class OpenGLText():
    # bitmap_fonts = [
    #     GLUT_BITMAP_9_BY_15,
    #     GLUT_BITMAP_8_BY_13,
    #     GLUT_BITMAP_TIMES_ROMAN_10,
    #     GLUT_BITMAP_TIMES_ROMAN_24,
    #     GLUT_BITMAP_HELVETICA_10,
    #     GLUT_BITMAP_HELVETICA_12,
    #     GLUT_BITMAP_HELVETICA_18]

    def print_bitmap_string(self, fonts,  s):
        for c in s:
            glutBitmapCharacter(fonts, * s)

    def TextOut(self, x, y, s):
        glRasterPos2f(x, y)
        self.print_bitmap_string(self.bitmap_fonts[4], s)


class Camera:
    origin = [0.0, 0.0, 0.0]
    length = 100.
    yangle = 0.
    zangle = 0.
    scaleFactor = 1.0
    __bthree = False

    def __init__(self):
        self.mouseLocation = [0.0, 0.0]
        self.offest = .1
        self.zangle = 0. if not self.__bthree else math.pi

    def setThirdPersonPerspective(self, value):
        self.__bthree = value
        self.zangle = self.zangle + math.pi
        self.yangle = -self.yangle

    def eye(self):
        return self.origin if not self.__bthree else self.direction()

    def target(self):
        return self.origin if self.__bthree else self.direction()

    def direction(self):
        if self.zangle > math.pi * 2.0:
            self.zangle = self.zangle - math.pi * 2.0
        elif self.zangle < 0.:
            self.zangle = self.zangle + math.pi * 2.0
        length = 1. if not self.__bthree else self.length if 0. else 1.
        xy = math.cos(self.yangle) * length
        x = self.origin[0] + xy * math.sin(self.zangle)
        y = self.origin[1] + length * math.sin(self.yangle)
        z = self.origin[2] + xy * math.cos(self.zangle)
        return [x, y, z]

    def move(self, x, y, z):
        sinz, cosz = math.sin(self.zangle), math.cos(self.zangle)
        xstep, zstep = x * cosz + z * sinz, z * cosz - x * sinz
        if self.__bthree:
            xstep = -xstep
            zstep = -zstep
        self.origin = [self.origin[0] + xstep, self.origin[1] + y, self.origin[2] + zstep]

    def rotate(self, z, y):
        self.zangle, self.yangle = self.zangle - z, self.yangle + y if not self.__bthree else -y

    def scale(self, step):
        self.scaleFactor += step
        if self.scaleFactor <= 0:
            self.scaleFactor = .01


    def setLookat(self):
        ve, vt = self.eye(), self.target()
        # print ve,vt
        glLoadIdentity()
        gluLookAt(ve[0], ve[1], ve[2], vt[0], vt[1], vt[2], 0.0, 1.0, 0.0)

    def keypress(self, key, x, y):
        key = key.decode('utf-8')
        if key in ('w', 'W'):
            self.move(0., 0., 1 * self.offest)
        if key in ('s', 'S'):
            self.move(0., 0., -1 * self.offest)
        if key in ('a', 'A'):
            self.move(1 * self.offest, 0., 0.)
        if key in ('d', 'D'):
            self.move(-1 * self.offest, 0., 0.)
        if key in ('q', 'Q'):
            self.move(0., 1 * self.offest, 0.)
        if key in ('e', 'E'):
            self.move(0., -1 * self.offest, 0.)
        if key in ('z', 'Z'):
            self.scale(self.offest)
        if key in ('x', 'X'):
            self.scale(-self.offest)
        if key in ('v', 'V'):
            # this.__bthree = not this.__bthree
            self.setThirdPersonPerspective(not self.__bthree)
        if key == GLUT_KEY_UP:
            self.offest = self.offest + 0.1
        if key == GLUT_KEY_DOWN:
            self.offest = self.offest - 0.1

    def mouse(self, x, y):
        rx = (x - self.mouseLocation[0]) * self.offest * 0.1
        ry = (y - self.mouseLocation[1]) * self.offest * -0.1
        self.rotate(rx, ry)
        self.mouseLocation = [x, y]

    def mouseFunc(self, button, mode, x, y):
        if button == GLUT_RIGHT_BUTTON:
            self.mouseLocation = [x, y]

    def mouseWheelFunc(self, ):
        pass


class OpenGLView():
    camera = Camera()
    MUTUAL_INFORMATION_FILE = '数据集/karate/mutualInformation.txt'

    def drawRandom(self):
        n, epochs, stacks, outer_radius, inner_radius = self.n, self.epochs, self.stacks, self.outer_radius, self.inner_radius
        theta, length = self.theta, self.length

        for e in range(epochs):
            glColor3f(0.0, 0.0, 1.0)
            glTranslate(0, 0, e/epochs-.5)
            for i in range(n):
                glTranslatef(np.cos(theta[i]-np.pi/2) * outer_radius, np.sin(theta[i]-np.pi/2) * outer_radius, 0.0)
                glRotatef(90, np.cos(theta[i]), np.sin(theta[i]), 0)

                quadratic = gluNewQuadric()
                gluCylinder(quadratic, inner_radius, inner_radius, .1+length[i], stacks, stacks)  # draw lateral of the cylinder
                # gluCylinder(quadratic, inner_radius, inner_radius, .1+length[i], stacks, stacks)  # draw lateral of the cylinder
                gluDisk(quadratic, 0, inner_radius, stacks, stacks)  # draw top and bottom

                glRotatef(-90, np.cos(theta[i]), np.sin(theta[i]), 0)
                glTranslate(-np.cos(theta[i]-np.pi/2) * outer_radius, -np.sin(theta[i]-np.pi/2) * outer_radius, 0.0)

            glColor3f(0.0, 1.0, 0.0)
            glutSolidTorus(inner_radius+.02, outer_radius, stacks, stacks)
            glTranslate(0, 0, -e / epochs+.5)

    def drawStatic(self):
        stacks, pointCountRecord, epochs, n, outer_radius, inner_radius, theta, length, colors = self.getData()
        for ei, e in enumerate(pointCountRecord):
            glTranslate(0, 0, ei / epochs - .5)
            for i in range(n):
                ci = e[str(i+1)][0]
                l = e[str(i+1)][1]
                glColor3f(colors[ci][0], colors[ci][1], colors[ci][2])
                glTranslatef(np.cos(theta[i]-np.pi/2) * outer_radius, np.sin(theta[i]-np.pi/2) * outer_radius, 0.0)
                glRotatef(90, np.cos(theta[i]), np.sin(theta[i]), 0)

                quadratic = gluNewQuadric()
                gluCylinder(quadratic, inner_radius, inner_radius, .1+l/epochs, stacks, stacks)  # draw lateral of the cylinder
                gluDisk(quadratic, 0, inner_radius, stacks, stacks)  # draw top and bottom

                glRotatef(-90, np.cos(theta[i]), np.sin(theta[i]), 0)
                glTranslate(-np.cos(theta[i]-np.pi/2) * outer_radius, -np.sin(theta[i]-np.pi/2) * outer_radius, 0.0)

            glColor3f(0.0, 1.0, 0.0)
            glutSolidTorus(inner_radius+.02, outer_radius, stacks, stacks)
            glTranslate(0, 0, -ei / epochs + .5)

    def drawDynamic(self):
        stacks, pointCountRecord, epochs, n, outer_radius, inner_radius, theta, length, colors = self.getData()
        self.index += 1
        for ei, e in enumerate(pointCountRecord[:(int(self.index / self.timeSpan) + 1) % epochs]):
            glTranslate(0, 0, ei / epochs - .5)
            for i in range(n):
                ci = e[str(i+1)][0]
                pl = e[str(i+1)][1]
                glColor3f(colors[ci][0], colors[ci][1], colors[ci][2])
                glTranslatef(np.cos(theta[i]-np.pi/2) * outer_radius, np.sin(theta[i]-np.pi/2) * outer_radius, 0.0)
                glRotatef(90, np.cos(theta[i]), np.sin(theta[i]), 0)

                quadratic = gluNewQuadric()
                gluCylinder(quadratic, inner_radius, inner_radius, .1+pl/epochs, stacks, stacks)  # draw lateral of the cylinder
                gluDisk(quadratic, 0, inner_radius, stacks, stacks)  # draw top and bottom

                glRotatef(-90, np.cos(theta[i]), np.sin(theta[i]), 0)
                glTranslate(-np.cos(theta[i]-np.pi/2) * outer_radius, -np.sin(theta[i]-np.pi/2) * outer_radius, 0.0)

            glColor3f(0.0, 1.0, 0.0)
            glutSolidTorus(inner_radius+.02, outer_radius, stacks, stacks)
            glTranslate(0, 0, -ei / epochs + .5)

    def drawFunc(self):
        # glRotatef(0.1, 0, 5, 0)  # (角度,x,y,z)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        self.camera.setLookat()
        glScalef(self.camera.scaleFactor, self.camera.scaleFactor, self.camera.scaleFactor)

        # self.drawRandom()
        # self.drawStatic()
        self.drawDynamic()

        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        glEnd()

        glFlush()
        glutSwapBuffers()


    def reshapeFunc(self, Width, Height):
        glViewport(0, 0, Width, Height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def openView(self):
        # 使用glut初始化OpenGL
        glutInit()
        # 显示模式:GLUT_SINGLE无缓冲直接显示|GLUT_RGBA采用RGB(A非alpha)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        # 窗口位置及大小-生成
        glutInitWindowPosition(0, 0)
        glutInitWindowSize(400, 400)
        w = glutCreateWindow(b"Algorithm View")
        # 调用函数绘制图像
        glutDisplayFunc(self.drawFunc)
        glutIdleFunc(self.drawFunc)
        # glutReshapeFunc(self.reshapeFunc)
        # 鼠标事件
        glutMouseFunc(self.camera.mouseFunc)
        # glutMouseWheelFunc(camera.mouseWheelFunc)
        glutMotionFunc(self.camera.mouse)
        glutKeyboardFunc(self.camera.keypress)
        glutSpecialFunc(self.camera.keypress)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glShadeModel(GL_SMOOTH)

        mat_specular = [1.0, 1.0, 1.0, 1.0]
        mat_shininess = [30.0]
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)  # 材质镜面反射
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)  # 材质高光

        white_light = [1.0, 1.0, 1.0, 1.0]
        Light_Model_Ambient = [0.2, 0.2, 0.2, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_POSITION, [-1, -1, -1, 0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, white_light)  # 漫反射
        glLightfv(GL_LIGHT0, GL_SPECULAR, white_light)  # 镜面反射
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, Light_Model_Ambient)  # 环境光

        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)

        self.initData()

        # 主循环
        # glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
        glutMainLoop()
        return w

    def initData(self):
        self.index = 0
        self.timeSpan = 30
        self.stacks = 30
        self.pointCountRecord = self.getCommunity()
        self.epochs = len(self.pointCountRecord)
        self.n = len(self.pointCountRecord[0].keys())

        self.outer_radius = .3
        self.inner_radius = self.outer_radius * 2 * np.pi / self.n
        self.theta = np.linspace(0, 2 * np.pi, self.n + 1)[:-1]
        self.length = np.random.rand(self.n)
        self.colors = [[np.random.rand(), np.random.rand(), np.random.rand()] for i in range(self.n)]

    def getData(self):
        return self.stacks, self.pointCountRecord, self.epochs, self.n, self.outer_radius, self.inner_radius, \
               self.theta, self.length, self.colors

    def getCommunity(self):
        lines = open(self.MUTUAL_INFORMATION_FILE, 'r').readlines()
        index = -1
        mutualInformation = []
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
        pointCountRecord = [{}]
        for ci, c in enumerate(communityCluster[0]):
            for p in str(c).split('  '):
                pointCountRecord[0][p] = [ci, 1]
        for ei, e in enumerate(communityCluster[1:]):
            pointCount =  deepcopy(pointCountRecord[ei]) # .copy()
            for ci, c in enumerate(e):
                for p in str(c).split('  '):
                    if pointCount[p][0] == ci:
                        pointCount[p][1] += 1
                    else:
                        if pointCount[p][1] <= 1:
                            pointCount[p] = [ci, 1]
                        else:
                            pointCount[p][1] -= 1
            pointCountRecord.append(pointCount)

        return pointCountRecord



if __name__ == "__main__":
    v = OpenGLView()
    v.getCommunity()
    v.openView()

#
#
# """GLUT-based fonts"""
# from OpenGL import GLUT
# from OpenGL.GL import *
# from OpenGLContext.scenegraph.text import fontprovider, font
# from OpenGLContext.arrays import *
# import logging
#
# log = logging.getLogger(__name__)
#
#
# class GLUTBitmapFont(font.NoDepthBufferMixIn, font.BitmapFontMixIn, font.Font):
#     """A GLUT-provided Bitmap Font
#
#     XXX current doesn't pay attention to fontStyle, should
#     get justification from it at least.
#     """
#
#     def __init__(self, fontStyle=None, specifier=None, charHeight=0):
#         """Initialise the bitmap font"""
#         self.fontStyle = fontStyle
#         if not specifier or not charHeight:
#             specifier, charHeight = GLUTFontProvider.match(fontStyle)
#         self.specifier = specifier
#         self._lineHeight = int(charHeight * 1.2)
#         self.charHeight = charHeight
#         self._displayLists = {}
#
#     def createChar(self, char, mode=None):
#         """Create the single-character display list
#         """
#         metrics = font.CharacterMetrics(
#             char,
#             GLUT.glutBitmapWidth(self.specifier, ord(char)),
#             self.charHeight
#         )
#         list = glGenLists(1)
#         glNewList(list, GL_COMPILE)
#         try:
#             try:
#                 if metrics.char != ' ':
#                     GLUT.glutBitmapCharacter(self.specifier, ord(char))
#                 else:
#                     glBitmap(0, 0, 0, 0, metrics.width, 0, None)
#             except Exception:
#                 glDeleteLists(list, 1)
#                 list = None
#         finally:
#             glEndList()
#         return list, metrics
#
#     def lists(self, value, mode=None):
#         """Get a sequence of display-list integers for value
#
#         Basically, this does a bit of trickery to do
#         as-required compilation of display-lists, so
#         that only those characters actually required
#         by the displayed text are compiled.
#
#         NOTE: Must be called from within the rendering
#         thread and within the rendering pass!
#         """
#         if __debug__:
#             log.info("""lists %s(%s)""", self, repr(value))
#         lists = []
#         for char in value:
#             list, metrics = self.getChar(char, mode=mode)
#             if list is not None:
#                 lists.append(list)
#         if __debug__:
#             log.info("""lists %s(%s)->%s""", self, repr(value), lists)
#         return lists
#
#     def lineHeight(self, mode=None):
#         """Retrieve normal line-height for this font
#         """
#         return self._lineHeight
#
#
# class _GLUTFontProvider(fontprovider.FontProvider):
#     """Singleton for creating new GLUTBitmapFonts
#     """
#     format = "bitmap"
#     scale = 12
#     bitmapFonts = {
#         'TYPEWRITER': (
#             (GLUT.GLUT_BITMAP_8_BY_13, 13),
#             (GLUT.GLUT_BITMAP_9_BY_15, 15),
#         ),
#         'SERIF': (
#             (GLUT.GLUT_BITMAP_TIMES_ROMAN_10, 10),
#             (GLUT.GLUT_BITMAP_TIMES_ROMAN_24, 24),
#         ),
#         'SANS': (
#             (GLUT.GLUT_BITMAP_HELVETICA_10, 10),
#             (GLUT.GLUT_BITMAP_HELVETICA_12, 12),
#             (GLUT.GLUT_BITMAP_HELVETICA_18, 18),
#         ),
#     }
#     bitmapFonts['ROMAN'] = bitmapFonts['SERIF']
#
#     def create(self, fontStyle, mode=None):
#         """Create a new font for the given fontStyle and mode"""
#         family, size = self.match(fontStyle, mode)
#         # get pre-existing font, register for this fontStyle
#         fontHash = self.fontHash(family, size)
#         if fontHash in self.fonts:
#             current = self.fonts.get(fontHash)
#             self.addFont(fontStyle, current)
#             return current
#         # no pre-existing, create
#         bitmapFont = GLUTBitmapFont(fontStyle, specifier=family, charHeight=size)
#         self.addFont(fontStyle, bitmapFont)
#         # extra registration for imprecise matching...
#         self.fonts[fontHash] = bitmapFont
#         return bitmapFont
#
#     def key(self, fontStyle=None):
#         """Calculate our "font key" for the fontStyle
#
#         If the font-key changes, we should be invalidating
#         our caches, but at the moment we aren't caching anything
#         3-D providers will add the various 3-D-specific fields
#         from the FontStyle3D node.
#         """
#         if not fontStyle:
#             return None
#         return (
#             tuple(fontStyle.family),
#             fontStyle.size,
#         )
#
#     def match(self, fontStyle=None, mode=None):
#         """Attempt to find matching font for our fontstyle
#
#         GLUT only provides a tiny number of fonts, so
#         this method is just scanning through the entire
#         set looking for something close.
#         """
#         # 10 point roman, closest to VRML semantics...
#         family, size = self.bitmapFonts.get("SERIF")[0]
#         if fontStyle and fontStyle.family:
#             current = None
#             for specifier in fontStyle.family:
#                 current = self.bitmapFonts.get(specifier.upper())
#             if current:
#                 # find closest size in the set of available sizes...
#                 target = fontStyle.size * self.scale
#                 diff, family, size = min([(abs(target - size), family, size) for (family, size) in current])
#                 if __debug__:
#                     if diff:
#                         log.info(
#                             """Using size %s for GLUT bitmap font, not equal to target %s""",
#                             size,
#                             target,
#                         )
#         return (family, size)
#
#     def enumerate(self, mode=None):
#         """Iterate through all available fonts (whether instantiated or not)
#
#         Just returns the bitmapFonts keys, which will
#         get each of the font-types which are available.
#         """
#         return self.bitmapFonts.keys()
#
#     def fontHash(family, size):
#         """Given family and size get hashable key for lookups
#
#         OpenGL-ctypes gives you the underlying GLUT font void*, whereas
#         PyOpenGL gave you an integer value
#         """
#         try:
#             hash((family, size))
#         except TypeError as err:
#             return (family.value, size)
#         else:
#             return (family, size)
#
#     fontHash = staticmethod(fontHash)
#
#
# GLUTFontProvider = _GLUTFontProvider()
# GLUTFontProvider.registerProvider(GLUTFontProvider)