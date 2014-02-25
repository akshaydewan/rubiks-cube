from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from time import time, sleep
from ctypes import *
import copy
import solcube
import solsteps
import logging
import sys
import pdb

logging.basicConfig(level=logging.WARNING)

#constants->
color = { 'white':[1,1,1,1],  
          'green':[0,1,0,1], 
          'orange':[1, 0.5, 0, 1], 
          'red':[1,0,0,1], 
          'blue':[0,0,1,1], 
          'yellow':[1,1,0,1],
          'black':[0,0,0,1] }
sqSize = 0.48
thick = 1.5 #dist of face from cube center
refCube = solcube.Cube()
uiCube = solcube.Cube()
lag = 0.02
drag_start_x = 0
drag_start_y = 0

class Rotate:
    z_angle = 0
    y_angle = 0
    x_angle = 0
    #face_angle = 0

def delay(start, n):
    while (time() - start < n):
        sleep(n - (time() - start))

def setColor(face, row, col):
    c = face.getSquare((row,col)).color
    glColor(color[c])

def goToFace(face, cube):
    if face==cube.up:
        glRotate(-90, 1,0,0)
    elif face==cube.down:
        glRotate(90, 1,0,0)
    elif face==cube.left:
        glRotate(-90, 0,1,0)
    elif face==cube.right:
        glRotate(90, 0,1,0)
    elif face==cube.front:
        pass
    elif face==cube.back:
        glRotate(180, 0,1,0)
    else:
        logging.error("Invalid face in drawFace()")
        sys.exit(1)
    glTranslate(0,0,thick)

def drawSquare(face, row, col):
    setColor(face, row, col)
    normal = [0,0,1]
    glBegin(GL_QUADS)
    glNormal3fv(normal)
    glVertex2f(-sqSize, -sqSize)
    glNormal3fv(normal)
    glVertex2f(-sqSize, sqSize)
    glNormal3fv(normal)
    glVertex2f(sqSize, sqSize)
    glNormal3fv(normal)
    glVertex2f(sqSize, -sqSize)
    glEnd()

def drawRow(face, row):
    glPushMatrix()
    if row==0:
        glTranslate(0,1,0)
    elif row==2:
        glTranslate(0,-1,0)
    drawSquare(face, row, 1)#middle
    glTranslate(1,0,0) 
    drawSquare(face, row, 2)#right
    glTranslate(-2,0,0) 
    drawSquare(face, row, 0)#left
    glPopMatrix()

def drawCol(face, col):
    glPushMatrix()
    if col==0:
        glTranslate(-1,0,0)
    elif col==2:
        glTranslate(1,0,0)
    drawSquare(face, 1, col) #middle
    glTranslate(0,1,0)
    drawSquare(face, 0, col) #top
    glTranslate(0,-2,0)
    drawSquare(face, 2, col) #bottom
    glPopMatrix()

def drawFace(face, cube):
    glPushMatrix()
    goToFace(face, cube)
    drawRow(face, 0) 
    drawRow(face, 1) 
    drawRow(face, 2)
    glPopMatrix()

def drawCube(cube):
    drawFace(cube.up, cube)
    drawFace(cube.down, cube)
    drawFace(cube.left, cube)
    drawFace(cube.right, cube)
    drawFace(cube.front, cube)
    drawFace(cube.back, cube)
    glColor(color['black'])
    glutSolidCube(2.9)

def moveUp(solving=False, inv=False):
    cube = uiCube
    adjFaces = [cube.front, cube.back, cube.left, cube.right]
    target = -91
    rate = -10
    if inv:
        target = -target
        rate = -rate
    for angle in range(0,target,rate):
        start = time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Rotating to current angle:
        glRotate(Rotate.y_angle, 0,1,0)
        glRotate(Rotate.x_angle, 1,0,0)
        #Drawing faces/squares that won't be changed:
        drawFace(cube.down, cube)
        for face in adjFaces:
            for row in [2,1]:
                glPushMatrix()
                goToFace(face, cube)
                drawRow(face, row)
                glPopMatrix()

        #Drawing the inside skeleton for existing items
        glColor(color['black'])
        
        glPushMatrix()
        glTranslate(0,-0.5,0)
        glScale(3,2,3)
        glutSolidCube(0.966)
        glPopMatrix()
    
        #drawing faces/squares that change, and animating them
        glPushMatrix()
        glRotate(angle, 0,1,0)
        drawFace(cube.up, cube)
        for face in adjFaces:
            glPushMatrix()
            goToFace(face, cube)
            drawRow(face, 0)
            glPopMatrix()
        glColor(color['black'])
        glTranslate(0,1,0)
        glScale(3,1,3)
        glutSolidCube(0.966)
        glPopMatrix()

        glutSwapBuffers()
        delay(start, lag)
        Rotate.x_angle = Rotate.y_angle = 0 #because I didn't push matrix
    if inv:
        cube.moveUpInv()
        if not solving:
            refCube.moveUpInv()
    else:
        cube.moveUp()
        if not solving:
            refCube.moveUp()

def moveDown(solving = False, inv=False):
    cube = uiCube
    adjFaces = [cube.front, cube.back, cube.left, cube.right]
    target = 91 #
    rate = 10 #
    if inv:
        target = -target
        rate = -rate
    for angle in range(0,target,rate):
        start = time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Rotating to current angle:
        glRotate(Rotate.y_angle, 0,1,0)
        glRotate(Rotate.x_angle, 1,0,0)
        #Drawing faces/squares that won't be changed:
        drawFace(cube.up, cube) #
        for face in adjFaces:
            for row in [0,1]: #
                glPushMatrix()
                goToFace(face, cube)
                drawRow(face, row)
                glPopMatrix()

        #Drawing the inside skeleton for existing items
        glColor(color['black'])
        
        glPushMatrix()
        glTranslate(0,0.5,0) #
        glScale(3,2,3)
        glutSolidCube(0.966)
        glPopMatrix()
    
        #drawing faces/squares that change, and animating them
        glPushMatrix()
        glRotate(angle, 0,1,0)
        drawFace(cube.down, cube) #
        for face in adjFaces:
            glPushMatrix()
            goToFace(face, cube)
            drawRow(face, 2) #
            glPopMatrix()
        glColor(color['black'])
        glTranslate(0,-1,0) #
        glScale(3,1,3)
        glutSolidCube(0.966)
        glPopMatrix()

        glutSwapBuffers()
        delay(start, lag)
        Rotate.x_angle = Rotate.y_angle = 0 #because I didn't push matrix
    if inv:
        cube.moveDownInv()
        if not solving:
            refCube.moveDownInv()
    else:
        cube.moveDown()
        if not solving:
            refCube.moveDown()

def moveFront(solving = False, inv=False):
    cube = uiCube
    adjFaces = [cube.up, cube.down, cube.left, cube.right]
    target = -91 #
    rate = -10 #
    if inv:
        target = -target
        rate = -rate
    for angle in range(0,target,rate):
        start = time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Rotating to current angle:
        glRotate(Rotate.y_angle, 0,1,0)
        glRotate(Rotate.x_angle, 1,0,0)
        #Drawing faces/squares that won't be changed:
        drawFace(cube.back, cube) #    
    
        face = cube.up
        for row in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawRow(face, row)
            glPopMatrix()

        face = cube.down
        for row in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawRow(face, row)
            glPopMatrix()

        face = cube.left
        for col in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.right
        for col in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        #Drawing the inside skeleton for existing items
        glColor(color['black'])        
        glPushMatrix()
        glTranslate(0,0,-0.5) #
        glScale(3,3,2)
        glutSolidCube(0.966)
        glPopMatrix()
    
        #drawing faces/squares that change, and animating them
        glPushMatrix()
        glRotate(angle, 0,0,1)
        drawFace(cube.front, cube) #

        face = cube.up
        glPushMatrix()
        goToFace(face, cube)
        drawRow(face, 2)
        glPopMatrix()

        face = cube.down
        glPushMatrix()
        goToFace(face, cube)
        drawRow(face, 0)
        glPopMatrix()

        face = cube.left
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 2)
        glPopMatrix()

        face = cube.right
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 0)
        glPopMatrix()

        glColor(color['black'])
        glPushMatrix()
        glTranslate(0,0,1)
        glScale(3,3,1)
        glutSolidCube(0.966)
        glPopMatrix()

        glPopMatrix()

        glutSwapBuffers()
        delay(start, lag)
        Rotate.x_angle = Rotate.y_angle = 0 #because I didn't push matrix
    if inv:
        cube.moveFrontInv()
        if not solving:
            refCube.moveFrontInv()
    else:
        cube.moveFront()
        if not solving:
            refCube.moveFront()

def moveBack(solving = False, inv=False):
    cube = uiCube
    adjFaces = [cube.up, cube.down, cube.left, cube.right]
    target = 91 #
    rate = 10 #
    if inv:
        target = -target
        rate = -rate
    for angle in range(0,target,rate):
        start = time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Rotating to current angle:
        glRotate(Rotate.y_angle, 0,1,0)
        glRotate(Rotate.x_angle, 1,0,0)
        #Drawing faces/squares that won't be changed:
        drawFace(cube.front, cube) #    
    
        face = cube.up
        for row in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawRow(face, row)
            glPopMatrix()

        face = cube.down
        for row in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawRow(face, row)
            glPopMatrix()

        face = cube.left
        for col in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.right
        for col in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        #Drawing the inside skeleton for existing items
        glColor(color['black'])        
        glPushMatrix()
        glTranslate(0,0,0.5) #
        glScale(3,3,2)
        glutSolidCube(0.966)
        glPopMatrix()
    
        #drawing faces/squares that change, and animating them
        glPushMatrix()
        glRotate(angle, 0,0,1)
        drawFace(cube.back, cube) #

        face = cube.up
        glPushMatrix()
        goToFace(face, cube)
        drawRow(face, 0)
        glPopMatrix()

        face = cube.down
        glPushMatrix()
        goToFace(face, cube)
        drawRow(face, 2)
        glPopMatrix()

        face = cube.left
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 0)
        glPopMatrix()

        face = cube.right
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 2)
        glPopMatrix()

        glColor(color['black'])
        glPushMatrix()
        glTranslate(0,0,-1)
        glScale(3,3,1)
        glutSolidCube(0.966)
        glPopMatrix()

        glPopMatrix()

        glutSwapBuffers()
        delay(start, lag)
        Rotate.x_angle = Rotate.y_angle = 0 #because I didn't push matrix
    if inv:
        cube.moveBackInv()
        if not solving:
            refCube.moveBackInv()
    else:
        cube.moveBack()
        if not solving:
            refCube.moveBack()

def moveRight(solving = False, inv=False):
    cube = uiCube
    adjFaces = [cube.up, cube.down, cube.front, cube.back]
    target = -91 #
    rate = -10 #
    if inv:
        target = -target
        rate = -rate
    for angle in range(0,target,rate):
        start = time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Rotating to current angle:
        glRotate(Rotate.y_angle, 0,1,0)
        glRotate(Rotate.x_angle, 1,0,0)
        #Drawing faces/squares that won't be changed:
        drawFace(cube.left, cube) #    
    
        face = cube.up
        for col in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.down
        for col in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.front
        for col in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.back
        for col in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        #Drawing the inside skeleton for existing items
        glColor(color['black'])        
        glPushMatrix()
        glTranslate(-0.5,0,0) #
        glScale(2,3,3)
        glutSolidCube(0.966)
        glPopMatrix()
    
        #drawing faces/squares that change, and animating them
        glPushMatrix()
        glRotate(angle, 1,0,0)
        drawFace(cube.right, cube) #

        face = cube.up
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 2)
        glPopMatrix()

        face = cube.down
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 2)
        glPopMatrix()

        face = cube.front
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 2)
        glPopMatrix()

        face = cube.back
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 0)
        glPopMatrix()

        glColor(color['black'])
        glPushMatrix()
        glTranslate(1,0,0)
        glScale(1,3,3)
        glutSolidCube(0.966)
        glPopMatrix()

        glPopMatrix()

        glutSwapBuffers()
        delay(start, lag)
        Rotate.x_angle = Rotate.y_angle = 0 #because I didn't push matrix
    if inv:
        cube.moveRightInv()
        if not solving:
            refCube.moveRightInv()        
    else:
        cube.moveRight()
        if not solving:
            refCube.moveRight()

def moveLeft(solving = False, inv=False):
    cube = uiCube
    adjFaces = [cube.up, cube.down, cube.front, cube.back]
    target = 91 #
    rate = 10 #
    if inv:
        target = -target
        rate = -rate
    for angle in range(0,target,rate):
        start = time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #Rotating to current angle:
        glRotate(Rotate.y_angle, 0,1,0)
        glRotate(Rotate.x_angle, 1,0,0)
        #Drawing faces/squares that won't be changed:
        drawFace(cube.right, cube) #    
    
        face = cube.up
        for col in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.down
        for col in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.front
        for col in [1,2]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        face = cube.back
        for col in [0,1]:
            glPushMatrix()
            goToFace(face, cube)
            drawCol(face, col)
            glPopMatrix()

        #Drawing the inside skeleton for existing items
        glColor(color['black'])        
        glPushMatrix()
        glTranslate(0.5,0,0) #
        glScale(2,3,3)
        glutSolidCube(0.966)
        glPopMatrix()
    
        #drawing faces/squares that change, and animating them
        glPushMatrix()
        glRotate(angle, 1,0,0)
        drawFace(cube.left, cube) #

        face = cube.up
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 0)
        glPopMatrix()

        face = cube.down
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 0)
        glPopMatrix()

        face = cube.front
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 0)
        glPopMatrix()

        face = cube.back
        glPushMatrix()
        goToFace(face, cube)
        drawCol(face, 2)
        glPopMatrix()

        glColor(color['black'])
        glPushMatrix()
        glTranslate(-1,0,0)
        glScale(1,3,3)
        glutSolidCube(0.966)
        glPopMatrix()

        glPopMatrix()

        glutSwapBuffers()
        delay(start, lag)
        Rotate.x_angle = Rotate.y_angle = 0 #because I didn't push matrix
    if inv:
        cube.moveLeftInv()
        if not solving:
            refCube.moveLeftInv()
    else:
        cube.moveLeft()
        if not solving:
            refCube.moveLeft()


def resetView():
    #logging.debug("Y angle: %f", Rotate.y_angle)
    #logging.debug("X angle: %f", Rotate.x_angle)
    #logging.debug("Z angle: %f", Rotate.z_angle)
    while Rotate.y_angle > 0: 
        Rotate.y_angle -= 10
        display()
    while Rotate.x_angle > 0:
        Rotate.x_angle -= 10
        display()
    while Rotate.z_angle > 0:
        Rotate.z_angle -= 10
        display()

    Rotate.x_angle = Rotate.y_angle = Rotate.z_angle = 0
    display()


def spin(solving=False):
    resetView()
    for i in range(9):
        start = time()
        Rotate.y_angle -= 10
        Rotate.y_angle = Rotate.y_angle%360
        display()
        delay(start, lag)
    if not solving:
        refCube.spin()
    uiCube.spin()
    Rotate.y_angle = 0

def rotateEW(solving=False):
    resetView()
    for i in range(9):
        start = time()
        Rotate.z_angle -= 10
        Rotate.z_angle = Rotate.z_angle%360
        display()
        delay(start, lag)
    if not solving:
        refCube.rotateEW()
    uiCube.rotateEW()
    Rotate.z_angle = 0

def rotateNS(solving = False):
    resetView()
    for i in range(9):
        start = time()
        Rotate.x_angle -= 10
        Rotate.x_angle = Rotate.x_angle%360
        display()
        delay(start, lag)
    if not solving:
        refCube.rotateNS()
    uiCube.rotateNS()
    Rotate.x_angle = 0


def solveCube():

    # print "---before solving---"
    # print "---RefCube---"
    # refCube.printFaces()
    # print "------"
    # print "---UI Cube---"
    # uiCube.printFaces()

    solving = True
    solver = solcube.Solver(refCube)
    solver.danBrown()
    moveList = solver.getSolutionSteps()
    print "--Before optimizing--"
    print moveList
    moveList = solsteps.SolutionSteps.basicOptimize(moveList)
    print "--After optimizing--"
    print moveList

    print "---after solving---"
    print "---RefCube---"
    refCube.printFaces()
    print "------"
    print "---UI Cube---"
    uiCube.printFaces()

    #junk = raw_input("next")

    for m in moveList:        
        performMove(m, solv=True)
    solving = False

    print "---after ui moving---"
    print "---RefCube---"
    refCube.printFaces()
    print "------"
    print "---UI Cube---"
    uiCube.printFaces()

def performMove(move,solv):
    """Perform a move"""
    mov = solsteps.Move
    if move == mov.up:
        moveUp(solving=solv)
    elif move == mov.upInv:
        moveUp(solving=solv, inv=True)
    elif move == mov.down:
        moveDown(solving=solv)
    elif move == mov.downInv:
        moveDown(solving=solv, inv=True)
    elif move == mov.left:
        moveLeft(solving=solv)
    elif move == mov.leftInv:
        moveLeft(solving=solv, inv=True)
    elif move == mov.right:
        moveRight(solving=solv)
    elif move == mov.rightInv:
        moveRight(solving=solv, inv=True)
    elif move == mov.front:
        moveFront(solving=solv)
    elif move == mov.frontInv:
        moveFront(solving = solv, inv=True)
    elif move == mov.back:
        moveBack(solving=solv)
    elif move == mov.backInv:
        moveBack(solving = solv, inv=True)
    elif move == mov.ns:
        rotateNS(solving=solv)
    elif move == mov.ew:
        rotateEW(solving=solv)
    elif move == mov.spin:
        spin(solving=solv)
    else:
        logging.warning("Unknown move in performMove()")

def shuffle(nMoves):
    """Starts shuffling a cube"""
    for i in range(nMoves):
        move = solsteps.Move.getRandomMove()
        performMove(move, solv=False)    


def init():
    glClearColor(1,1,1,1)
    glLight(GL_LIGHT0, GL_POSITION, [0,0,4])
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    # glEnable(GL_POLYGON_SMOOTH)
    # glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    # glEnable(GL_LINE_SMOOTH)
    # glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    # glEnable(GL_POINT_SMOOTH)
    # glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glPushMatrix()
    glRotate(Rotate.y_angle, 0,1,0)
    glRotate(Rotate.x_angle, 1,0,0)
    glRotate(Rotate.z_angle, 0,0,1)
    drawCube(uiCube)
    glPopMatrix()
    
    glutSwapBuffers()

def reshape(w,h):
    glViewport(0,0,w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 1,30)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(2, 2, 6, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

def moveByColor(color, inv=False):
    face = uiCube.getDirection(color)
    if face == uiCube.up:
        moveUp(inv=inv)
    elif face == uiCube.down:
        moveDown(inv=inv)
    elif face == uiCube.front:
        moveFront(inv=inv)
    elif face == uiCube.back:
        moveBack(inv=inv)
    elif face == uiCube.left:
        moveLeft(inv=inv)
    elif face == uiCube.right:
        moveRight(inv=inv)
    else:
        logging.error("Invalid color in moveByColor")
    
def keyboard(key, x, y):
    if key == 'r':
        moveByColor('red')
    elif key == 'R':
        moveByColor('red', inv=True)
    elif key == 'y':
        moveByColor('yellow')
    elif key == 'Y':
        moveByColor('yellow', inv=True)
    elif key == 'g':
        moveByColor('green')
    elif key == 'G':
        moveByColor('green', inv=True)
    elif key == 'o':
        moveByColor('orange')
    elif key == 'O':
        moveByColor('orange', inv=True)
    elif key == 'w':
        moveByColor('white')
    elif key == 'W':
        moveByColor('white', inv=True)
    elif key == 'b':
        moveByColor('blue')
    elif key == 'B':
        moveByColor('blue', inv=True)
    elif key == 's':
        shuffle(5)
    elif key == ' ':
        solveCube()

    # if key=='r':
    #     Rotate.y_angle += 10
    #     if Rotate.y_angle >= 360:
    #         Rotate.y_angle = Rotate.y_angle - 360
    #     glutPostRedisplay()
    # elif key=='R':
    #     Rotate.x_angle += 10
    #     if Rotate.x_angle >= 360:
    #         Rotate.x_angle = Rotate.x_angle - 360
    #     glutPostRedisplay()
    # elif key=='s':
    #     spin()
    # elif key=='a':
    #     rotateEW()
    # elif key=='d':
    #     rotateNS()
    # elif key=='1':
    #     moveUp(inv=False)
    # elif key=='!':
    #     moveUp(inv=True)
    # elif key=='2':
    #     moveDown(inv=False)
    # elif key=='@':
    #     moveDown(inv=True)
    # elif key=='3':
    #     moveFront(inv=False)
    # elif key=='#':
    #     moveFront(inv=True)
    # elif key=='4':
    #     moveBack(inv=False)
    # elif key=='$':
    #     moveBack(inv=True)
    # elif key=='5':
    #     moveRight(inv=False)
    # elif key=='%':
    #     moveRight(inv=True)
    # elif key=='6':
    #     moveLeft(inv=False)
    # elif key=='^':
    #     moveLeft(inv=True)
    # elif key==' ':
    #     solveCube()
    # elif key=='p':
    #     shuffle(5);            

def processMouse(button, state, x, y):
    global drag_start_y
    global drag_start_x
    if state==GLUT_DOWN and button == GLUT_LEFT_BUTTON:
        drag_start_x = x
        drag_start_y = y
        #logging.debug("drag start x: %d", x)
        #logging.debug("drag start y: %d", y)

def processMouseActiveMotion(x, y):
    # Note: There is no multiplier used for the delta value
    # It is directly used as the angle.
    # The window size is 400px, which is close to 360, so this works fine (or so I think)
    global drag_start_x
    global drag_start_y
    delta_x = drag_start_x - x
    delta_y = drag_start_y - y

    if delta_y < 0:
        Rotate.x_angle += abs(delta_y)
    else:
        Rotate.x_angle -= abs(delta_y)

    if delta_x < 0:
        Rotate.y_angle += abs(delta_x)
    else:
        Rotate.y_angle -= abs(delta_x)

    if Rotate.y_angle >= 360:
        Rotate.y_angle = Rotate.y_angle - 360
    elif Rotate.y_angle < 0:
        Rotate.y_angle += 360

    if Rotate.x_angle >= 360:
        Rotate.x_angle = Rotate.x_angle - 360
    elif Rotate.x_angle < 0:
        Rotate.x_angle += 360

    drag_start_x = x
    drag_start_y = y
    glutPostRedisplay()

    #logging.debug("Rotate x angle: %f", Rotate.x_angle)
    #logging.debug("Rotate y angle: %f", Rotate.y_angle)
    #logging.debug("Mouse x: %f", x)
    #logging.debug("Mouse y: %f", y)

# def showMenu():
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

def createMenu():
    MENUFUNC = CFUNCTYPE(void, c_int)
    menuFunc = MENUFUNC(processMenuEvents)
    menu = glutCreateMenu(menuFunc)
    glutAddMenuEntry("One", 1)
    glutAddMenuEntry("Two", 2)
    glutAttachMenu(GLUT_RIGHT_BUTTON)
    
def processMenuEvents(option):
    logging.debug("Menu pressed: %d", option)

if __name__=="__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_MULTISAMPLE)
    glutInitWindowSize(400,400)
    glutInitWindowPosition(100,100)

    mainWindow = glutCreateWindow(sys.argv[0])
    #init()
    #glutDisplayFunc(display)
    #glutReshapeFunc(reshape)
    #glutKeyboardFunc(keyboard)

    #subWindow = glutCreateSubWindow(mainWindow, 0, 0, 400, 400)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(processMouse)
    glutMotionFunc(processMouseActiveMotion)
    createMenu()
    init()

    glutMainLoop()
    
    
