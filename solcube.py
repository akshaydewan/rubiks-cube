#!/usr/bin/env python

import sys
import copy
import random
import logging
import pdb
import solsteps

logging.basicConfig(level=logging.WARNING)

solutionSteps = solsteps.SolutionSteps()
move = solsteps.Move

class Square:
    """Represents a single square(2D) of the cube"""
    def __init__(self, color):
        self.color = color
        self.edge = None
        self.corner = None

    def setPos(self, pos):
        """Set the position of the square"""
        self.pos = pos #tuple

    def setFace(self, face):
        """Set the current face of the square"""
        self.face = face

    def setEdge(self, edge):
        """Sets the edge that the square belongs to"""
        self.edge = edge
        
    def setCorner(self, corner):
        """Sets the corner that the square belongs to"""
        self.corner = corner

    def createCopy(self):
        """Creates a copy of the square"""
        copiedSquare = Square(self.color)
        return copiedSquare

class Edge:
    """Represents an edge consisting of two squares"""
    
    edgeLocations=[(0,1),(1,0),(1,2),(2,1)]    

    def __init__(self, sq1, sq2, layer):
        self.squares = (sq1,sq2)
        self.layer = layer
        sq1.setEdge(self)
        sq2.setEdge(self)

    def createCopy(self, sq1, sq2):
        """Creates a copy of the edge"""
        copiedEdge = Edge(sq1, sq2, self.layer)
        return copiedEdge

    def getCenterColors(self):
        """Get the colors of the faces of the edge squares"""
        return [self.squares[0].face.getSquare((1,1)).color, self.squares[1].face.getSquare((1,1)).color]

    def isAligned(self, color):
        """Checks if the edge is at its proper position (but not necessarily in its right orientation"""
        centerColors = self.getCenterColors()
        if self.squares[0].color==color:
            edgeColor = self.squares[1].color #because aligning to the 'target' color is impossible
        else:
            edgeColor = self.squares[0].color
        if edgeColor in centerColors:
            return True
        else:
            return False

    def align(self, cube, color):
        """Aligns the edge to its face (but does not orient)"""
        for i in range(4):
            if self.isAligned(color):
                return
            else:
                if self.layer==0:
                    cube.moveUp()
                elif self.layer==2:
                    cube.moveDown()
           #may need to elaborate later
        logging.error("Edge.align(), cannot align edge")
        sys.exit(1)

    def isOriented(self):
        """Checks if an aligned edge is oriented to its proper face"""
        centerColors = self.getCenterColors()
        if self.squares[0].color==centerColors[0] and self.squares[1].color==centerColors[1]:
            return True
        else:
            return False
        
    # def isSolved(self, color): #TODO: consider removal of this
    #     """Checks if the edge is in 'solved' position"""
    #     if self.isAligned(color) and self.isOriented():
    #         return True
    #     else:
    #         return False

    def bringToTop(self, cube):
        """Bring the edge to the top layer"""
        face0 = self.squares[0].face
        face1 = self.squares[1].face
        if face0==cube.down:
            cube.move(face1, 2)
        else:
            cube.move(face0, 2)

    def bringToBottom(self, cube, color):
        """brings the edge to the bottom layer"""
        if self.layer==1:
            if self.squares[0].color==color:
                while self.layer!=2:
                    cube.move(self.squares[1].face)
            else:
                while self.layer!=2:
                    cube.move(self.squares[0].face)
        elif self.layer==0:
            if self.squares[0].face==cube.up:
                while self.layer!=2:
                    cube.move(self.squares[1].face)
            else:
                while self.layer!=2:
                    cube.move(self.squares[0].face)

    @staticmethod
    def updateEdgeLayers(cube, faceList):
        """Updates the layer in which the edge belongs"""
        for face in faceList:
            for e in Edge.edgeLocations:
                sq = face.getSquare(e)
                if sq.face==cube.up:
                    sq.edge.layer = 0
                elif sq.face==cube.down:
                    sq.edge.layer = 2
                else:
                    sq.edge.layer = e[0] #the row in which the edge lies

    @staticmethod
    def checkEdges(face):
        """Check if edges are proper""" #for testing
        for e in Edge.edgeLocations:
            if face.getSquare(e).edge==None:
                print e, "No Edge set!"
            else:
                print "ok"
        

class Corner:
    """Represents a corner consisting of three squares"""

    cornerLocations = [(0,0),(0,2),(2,0),(2,2)]

    def __init__(self, sq1, sq2, sq3, layer):
        # self.sq1 = sq1
        # self.sq2 = sq2
        # self.sq3 = sq3
        self.squares = (sq1,sq2,sq3)
        self.layer = layer
        sq1.setCorner(self)
        sq2.setCorner(self)
        sq3.setCorner(self)
    
    def createCopy(self, sq1, sq2, sq3):
        """Creates a copy of the Corner"""
        copiedCorner = Corner(sq1, sq2, sq3, self.layer)
        return copiedCorner

    def getCenterColors(self):
        """Get the colors of the center faces of the squares"""
        center0 = self.squares[0].face.getSquare((1,1))
        center1 = self.squares[1].face.getSquare((1,1))
        center2 = self.squares[2].face.getSquare((1,1))
        centerColors = [center0.color, center1.color, center2.color]
        return centerColors

    def getSquareColors(self):
        """Get the colors of the squares of the corner"""
        return [self.squares[0].color, self.squares[1].color, self.squares[2].color]

    def isInPlace(self):
        """Checks if the corner is in its proper place (but not necessarily oriented"""
        centerColors = set(self.getCenterColors())
        squareColors = set(self.getSquareColors())
        if centerColors==squareColors:
            return True
        else:
            return False      

    def isOriented(self):
        """Checks if the corners are properly oriented"""
        centerColors = self.getCenterColors()
        squareColors = self.getSquareColors()
        if centerColors==squareColors:
            return True
        else:
            return False        

    def alignUnder(self, color, cube):
        """Align a corner under its target position"""
        squareColors = set(self.getSquareColors())
        squareColors.remove(color) #'color' face will always be on top, will never align
        centerColors = set(self.getCenterColors())
        for i in range(4):
            if squareColors.issubset(centerColors):
                return
            else:
                cube.moveDown()
                centerColors = set(self.getCenterColors())
        logging.error("alignUnder() failed for %s - %s", squareColors, color)
        sys.exit(1)

    def upFaceColor(self, cube):
        """Returns the color of the square in the up face"""
        if self.layer!=0:
            logging.error("upFaceColor(): corner not in top layer!")
            sys.exit(1)
        for sq in self.squares:
            if sq.face==cube.up:
                return sq.color
                           
    @staticmethod
    def updateCornerLayers(cube, faceList):
        """Update the layer of the corners of the given face"""
        for face in faceList:
            for c in Corner.cornerLocations:
                sq = face.getSquare(c)
                if sq.face==cube.up:
                    sq.corner.layer = 0
                elif sq.face==cube.down:
                    sq.corner.layer = 2
                else:
                    sq.corner.layer = c[0] #The row in which the square lies

    @staticmethod
    def printCorners(cube):
        """Prints the corners of the cube""" #for testing
        for corner in cube.cornerList:
            for i in range(3):
                print corner.squares[i].color,
                print corner.squares[i].pos,
                if corner.squares[i].face==cube.up:
                    print 'up'
                elif corner.squares[i].face==cube.down:
                    print 'down'
                elif corner.squares[i].face==cube.left:
                    print 'left'
                elif corner.squares[i].face==cube.right:
                    print 'right'
                elif corner.squares[i].face==cube.front:
                    print 'front'
                elif corner.squares[i].face==cube.back:
                    print 'back'
            print

class Face:
    """Cube Face"""
    def __init__(self, face):
        self.face = face
        for row in [0,1,2]:
            for col in [0,1,2]:
                self.face[row][col].setFace(self)
                self.face[row][col].setPos((row,col)) #tuple

    def createCopy(self):
        """Returns a copy of the face"""        
        copiedFace = Face(self.deepCopy())
        for row in [0,1,2]:
            for col in [0,1,2]:
                copiedFace.face[row][col] = self.face[row][col].createCopy()
                copiedFace.face[row][col].setFace(copiedFace)
                copiedFace.face[row][col].setPos((row,col)) #tuple
        return copiedFace


    def deepCopy(self):
        """Returns a copy of the current face"""
        #not using copy.deepcopy because it causes problems
        returnFace = []
        for i in [0,1,2]:
            returnFace.append(copy.copy(self.face[i]))
        return returnFace

    def rotateClockwise(self):
        """Rotate a face clockwise in a single plane"""
        tempFace = self.deepCopy()
        k = 3
        for i in [0,1,2]:
            k = k-1
            for j in [0,1,2]:
                self.face[j][k] = tempFace[i][j]
                self.face[j][k].setPos((j,k))
    
    def rotateCounterClockwise(self):
        """Rotate a face counterclockwise in a single plane"""
        tempFace = self.deepCopy()
        for i in [0,1,2]:
            k = 3
            for j in [0,1,2]:
                k = k-1
                self.face[k][i] = tempFace[i][j]
                self.face[k][i].setPos((k,i))

    def row(self, nRow):
        """Return the row of a face as a list"""
        return self.face[nRow]

    def col(self, nCol):
        """Return the column of a face as a list"""
        returnCol = []
        for i in [0,1,2]:
            returnCol.append(self.face[i][nCol])
        return returnCol

    def getSquare(self, pos):
        """Return the square at (i,j) position"""
        return self.face[pos[0]][pos[1]]

    def setRow(self, nRow, srcRow):
        """Set the row of a face as given in the srcRow"""
        self.face[nRow] = copy.copy(srcRow)
        nCol = 0
        for square in self.face[nRow]:
            square.setFace(self)
            square.setPos((nRow, nCol))
            nCol = nCol + 1

    def setCol(self, nCol, srcCol):
        """Set the column of a face as given in the srcCol"""
        for i in [0,1,2]:
            self.face[i][nCol] = srcCol[i]
            self.face[i][nCol].setPos((i,nCol))
        self.updateSquareFace(col=[nCol])

    def reverseRow(self, row):
        """Reverses the row of the specified face"""
        self.face[row].reverse()
        oldCol=[0,1,2]
        newCol=[2,1,0]
        for col in oldCol:
            self.face[row][col].setPos((row, newCol[col]))

    def reverseCol(self, nCol):
        """reverses the column of the specified face"""
        tempCol = self.col(nCol)
        tempCol.reverse()
        self.setCol(nCol, tempCol)

    def deepReverse(self):
        """reverses rows, followed by columns
        [[1,2,3],[4,5,6],[7,8,9] -> [[9,8,7],[6,5,4],[3,2,1]]"""
        self.face.reverse()
        for i in [0,1,2]:
            self.reverseRow(i)

    def updateSquareFace(self, row=[0,1,2], col=[0,1,2]):
        """Updates the face of specified squares to 'self.face'"""
        for r in row:
            for c in col:
                self.face[r][c].setFace(self)

    def printFace(self):
        """Prints the face on the commandline"""
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.face[i][j].color[0],
            print

    def hasLine(self):
        """Checks if the face has a 'Line' formation"""
        centerColor = self.getSquare((1,1)).color
        #line1 = [(0,1),(2,1)]
        #line2 = [(1,0),(1,2)]
        color1 = [self.face[0][1].color, self.face[2][1].color]
        color2 = [self.face[1][0].color, self.face[1][2].color]
        if set(color1)==set([centerColor]) or set(color2)==set([centerColor]):
            return True
        else:
            return False


class Cube:
    """The main Rubik's cube class"""
    def __init__(self):
        w = []
        r = []
        g = []
        o = []
        b = []
        y = []
        for i in range(9):
            w.append(Square('white'))
            r.append(Square('red'))
            g.append(Square('green'))
            o.append(Square('orange'))
            b.append(Square('blue'))
            y.append(Square('yellow'))
            
        self.white = Face([ [w[0], w[1], w[2]],
                            [w[3], w[4], w[5]],
                            [w[6], w[7], w[8]] ])
        self.red = Face([ [r[0], r[1], r[2]],
                          [r[3], r[4], r[5]],
                          [r[6], r[7], r[8]] ])
        self.green =  Face([ [g[0], g[1], g[2]],
                             [g[3], g[4], g[5]],
                             [g[6], g[7], g[8]] ])
        self.orange =  Face([ [o[0], o[1], o[2]],
                              [o[3], o[4], o[5]],
                              [o[6], o[7], o[8]] ])
        self.blue =  Face([ [b[0], b[1], b[2]],
                            [b[3], b[4], b[5]],
                            [b[6], b[7], b[8]] ])
        self.yellow =  Face([ [y[0], y[1], y[2]],
                              [y[3], y[4], y[5]],
                              [y[6], y[7], y[8]] ])
        self.faceList = [self.white, self.red, self.green, self.blue, self.orange, self.yellow]
        self.up = self.white
        self.back = self.red
        self.right = self.green
        self.front = self.orange
        self.left = self.blue
        self.down = self.yellow
        self.faceDirectionList = [self.up, self.back, self.right, self.front, self.left, self.down]
        self.edgeRW = Edge(r[1], w[1], 0) #top-back
        self.edgeGW = Edge(g[1], w[5], 0) #top-right
        self.edgeOW = Edge(o[1], w[7], 0) #top-front
        self.edgeBW = Edge(b[1], w[3], 0) #top-left
        self.edgeBO = Edge(b[5], o[3], 1) #front-left
        self.edgeGO = Edge(g[3], o[5], 1) #front-right
        self.edgeGR = Edge(g[5], r[3], 1) #back-right
        self.edgeBR = Edge(b[3], r[5], 1) #back-left
        self.edgeOY = Edge(o[7], y[1], 2) #front-down
        self.edgeGY = Edge(g[7], y[5], 2) #right-down
        self.edgeBY = Edge(b[7], y[3], 2) #left-down
        self.edgeRY = Edge(r[7], y[7], 2) #back-down
        self.edgeList = [self.edgeRW, self.edgeGW, self.edgeOW, self.edgeBW, self.edgeBO, self.edgeGO, self.edgeGR, self.edgeBR, self.edgeOY, self.edgeGY, self.edgeBY, self.edgeRY]
        self.cornerBOW = Corner(b[2], o[0], w[6], 0) #up-front-left
        self.cornerGOW = Corner(g[0], o[2], w[8], 0) #up-front-right
        self.cornerBRW = Corner(b[0], r[2], w[0], 0) #up-back-left
        self.cornerGRW = Corner(g[2], r[0], w[2], 0) #up-back-right
        self.cornerBOY = Corner(b[8], o[6], y[0], 2) #down-front-left
        self.cornerGOY = Corner(g[6], o[8], y[2], 2) #down-front-right
        self.cornerBRY = Corner(b[6], r[8], y[6], 2) #down-back-left
        self.cornerGRY = Corner(g[8], r[6], y[8], 2) #down-back-right
        self.cornerList = [self.cornerBOW, self.cornerGOW, self.cornerBRW, self.cornerGRW, self.cornerBOY, self.cornerGOY, self.cornerBRY, self.cornerGRY]
        
    def createCopy(self):
        """Create a copy of the cube"""
        copiedCube = Cube()


        copiedCube.white = self.white.createCopy()
        copiedCube.red = self.red.createCopy()
        copiedCube.green = self.green.createCopy()
        copiedCube.orange = self.orange.createCopy()
        copiedCube.blue = self.blue.createCopy
        copiedCube.yellow = self.yellow.createCopy
        copiedCube.faceList = [copiedCube.white, copiedCube.red, copiedCube.green, copiedCube.blue, copiedCube.orange, copiedCube.yellow]

        copiedCube.up = self.up.createCopy()
        copiedCube.back = self.back.createCopy()
        copiedCube.right = self.right.createCopy()
        copiedCube.front = self.front.createCopy()
        copiedCube.left = self.left.createCopy()
        copiedCube.down = self.down.createCopy()
        copiedCube.faceDirectionList = [copiedCube.up, copiedCube.back, copiedCube.right, copiedCube.front, copiedCube.left, copiedCube.down]

        copiedCube.edgeRW = self.edgeRW.createCopy()
        copiedCube.edgeGW = self.edgeGW.createCopy()
        copiedCube.edgeOW = self.edgeOW.createCopy()
        copiedCube.edgeBW = self.edgeBW.createCopy()
        copiedCube.edgeBO = self.edgeBO.createCopy()
        copiedCube.edgeGO = self.edgeGO.createCopy()
        copiedCube.edgeGR = self.edgeGR.createCopy()
        copiedCube.edgeBR = self.edgeBR.createCopy()
        copiedCube.edgeOY = self.edgeOY.createCopy()
        copiedCube.edgeGY = self.edgeGY.createCopy()
        copiedCube.edgeBY = self.edgeBY.createCopy()
        copiedCube.edgeRY = self.edgeRY.createCopy()
        copiedCube.edgeList = [copiedCube.edgeRW, copiedCube.edgeGW, copiedCube.edgeOW, copiedCube.edgeBW, copiedCube.edgeBO, copiedCube.edgeGO, copiedCube.edgeGR, copiedCube.edgeBR, copiedCube.edgeOY, copiedCube.edgeGY, copiedCube.edgeBY, copiedCube.edgeRY]

        copiedCube.cornerBOW = self.cornerBOW.createCopy()
        copiedCube.cornerGOW = self.cornerGOW.createCopy()
        copiedCube.cornerBRW = self.cornerBRW.createCopy()
        copiedCube.cornerGRW = self.cornerGRW.createCopy()
        copiedCube.cornerBOY = self.cornerBOY.createCopy()
        copiedCube.cornerGOY = self.cornerGOY.createCopy()
        copiedCube.cornerBRY = self.cornerBRY.createCopy()
        copiedCube.cornerGRY = self.cornerGRY.createCopy()
        copiedCube.cornerList = [copiedCube.cornerBOW, copiedCube.cornerGOW, copiedCube.cornerBRW, copiedCube.cornerGRW, copiedCube.cornerBOY, copiedCube.cornerGOY, copiedCube.cornerBRY, copiedCube.cornerGRY]


        # copiedFaceList = []
        # for face in self.faceList:
        #     copiedFaceList.append(face.createCopy())
        # copiedCube.faceList = copiedFaceList

        # copiedFaceDirectionList = []
        # for face in self.faceDirectionList:
        #     copiedFaceDirectionList.append(face.createCopy())
        # copiedCube.faceDirectionList = copiedFaceDirectionList

        # copiedEdgeList = []
        # for edge in self.edgeList:
        #     copiedEdgeList.append(edge.createCopy())
        # copiedCube.edgeList = copiedEdgeList

        # copiedCornerList = []
        # for corner in self.cornerList:
        #     copiedCornerList.append(corner.createCopy())
        # copiedCube.cornerList = copiedCornerList

        return copiedCube


    def moveUp(self):
        """Rotate the self.up face clockwise"""
        logging.debug("Performing moveUp()")
        self.up.rotateClockwise()
        tempRow = copy.copy(self.right.row(0))
        self.right.setRow(0, self.back.row(0))
        self.back.setRow(0, self.left.row(0))
        self.left.setRow(0, self.front.row(0))
        self.front.setRow(0, tempRow)
        solutionSteps.moveList.append(move.up)
        
        
    def moveUpInv(self):
        """Rotate the self.up face counterclockwise"""
        logging.debug("Performing moveUpInv()")
        self.up.rotateCounterClockwise()
        tempRow = copy.copy(self.left.row(0))
        self.left.setRow(0, self.back.row(0))
        self.back.setRow(0, self.right.row(0))
        self.right.setRow(0, self.front.row(0))
        self.front.setRow(0, tempRow)
        solutionSteps.moveList.append(move.upInv)

    def moveDown(self):
        """Rotate the self.down face clockwise"""
        logging.debug("Performing moveDown()")
        self.down.rotateClockwise()
        tempRow = copy.copy(self.left.row(2))
        self.left.setRow(2, self.back.row(2))
        self.back.setRow(2, self.right.row(2))
        self.right.setRow(2, self.front.row(2))
        self.front.setRow(2, tempRow)
        solutionSteps.moveList.append(move.down)
        
    def moveDownInv(self):
        """Rotate the self.down face counterclockwise"""
        logging.debug("Performing moveDownInv()")
        self.down.rotateCounterClockwise()
        tempRow = copy.copy(self.right.row(2))
        self.right.setRow(2, self.back.row(2))
        self.back.setRow(2, self.left.row(2))
        self.left.setRow(2, self.front.row(2))
        self.front.setRow(2, tempRow)
        solutionSteps.moveList.append(move.downInv)

    def moveLeft(self):
        """Rotate the left face clockwise"""
        logging.debug("Performing moveLeft()")
        self.left.rotateClockwise()
        tempCol = self.front.col(0)
        self.front.setCol(0, self.up.col(0))
        self.up.setCol(0, self.back.col(2))
        self.up.reverseCol(0)
        self.back.setCol(2, self.down.col(0))
        self.back.reverseCol(2)
        self.down.setCol(0, tempCol)
        Edge.updateEdgeLayers(self, [self.left])
        Corner.updateCornerLayers(self, [self.left])
        solutionSteps.moveList.append(move.left)
        
    def moveLeftInv(self):
        """Rotate the left face counterclockwise"""
        logging.debug("Performing moveLeftInv()")
        self.left.rotateCounterClockwise()
        tempCol = self.back.col(2)
        self.back.setCol(2, self.up.col(0))
        self.back.reverseCol(2)
        self.up.setCol(0, self.front.col(0))
        self.front.setCol(0, self.down.col(0))
        self.down.setCol(0, tempCol)
        self.down.reverseCol(0)
        Edge.updateEdgeLayers(self, [self.left])
        Corner.updateCornerLayers(self, [self.left])
        solutionSteps.moveList.append(move.leftInv)

    def moveRight(self):
        """Rotate the right face clockwise"""
        logging.debug("Performing moveRight()")
        self.right.rotateClockwise()
        tempCol = self.back.col(0)
        self.back.setCol(0, self.up.col(2))
        self.back.reverseCol(0)
        self.up.setCol(2, self.front.col(2))
        self.front.setCol(2, self.down.col(2))
        self.down.setCol(2, tempCol)
        self.down.reverseCol(2)
        Edge.updateEdgeLayers(self, [self.right])
        Corner.updateCornerLayers(self, [self.right])
        solutionSteps.moveList.append(move.right)
               
    def moveRightInv(self):
        """Rotate the right face counterclockwise"""
        logging.debug("Performing moveRightInv()")
        self.right.rotateCounterClockwise()
        tempCol = self.front.col(2)
        self.front.setCol(2, self.up.col(2))
        self.up.setCol(2, self.back.col(0))
        self.up.reverseCol(2)
        self.back.setCol(0, self.down.col(2))
        self.back.reverseCol(0)
        self.down.setCol(2, tempCol)
        Edge.updateEdgeLayers(self, [self.right])
        Corner.updateCornerLayers(self, [self.right])
        solutionSteps.moveList.append(move.rightInv)

    def moveFront(self):
        """Rotate the front face clockwise"""
        logging.debug("Performing moveFront()")
        self.front.rotateClockwise()
        tempCol = self.right.col(0)
        self.right.setCol(0, self.up.row(2))
        self.up.setRow(2, self.left.col(2))
        self.up.reverseRow(2)
        self.left.setCol(2, self.down.row(0))
        self.down.setRow(0, tempCol)
        self.down.reverseRow(0)
        Edge.updateEdgeLayers(self, [self.front])
        Corner.updateCornerLayers(self, [self.front])
        solutionSteps.moveList.append(move.front)

    def moveFrontInv(self):
        """Rotate the front face counterclockwise"""
        logging.debug("Performing moveFrontInv()")
        self.front.rotateCounterClockwise()
        tempCol = self.left.col(2)
        self.left.setCol(2, self.up.row(2))
        self.left.reverseCol(2)
        self.up.setRow(2, self.right.col(0))
        self.right.setCol(0, self.down.row(0))
        self.right.reverseCol(0)
        self.down.setRow(0, tempCol)
        Edge.updateEdgeLayers(self, [self.front])
        Corner.updateCornerLayers(self, [self.front])
        solutionSteps.moveList.append(move.frontInv)
        
    def moveBack(self):
        """Rotate the back face clockwise"""
        logging.debug("Performing moveBack()")
        self.back.rotateClockwise()
        tempCol = self.left.col(0)
        self.left.setCol(0, self.up.row(0))
        self.left.reverseCol(0)
        self.up.setRow(0, self.right.col(2))
        self.right.setCol(2, self.down.row(2))
        self.right.reverseCol(2)
        self.down.setRow(2, tempCol)
        Edge.updateEdgeLayers(self, [self.back])
        Corner.updateCornerLayers(self, [self.back])
        solutionSteps.moveList.append(move.back)

    def moveBackInv(self):
        """Rotate the back face counterclockwise"""
        logging.debug("Performing moveBackInv()")
        self.back.rotateCounterClockwise()
        tempCol = self.right.col(2)
        self.right.setCol(2, self.up.row(0))
        self.up.setRow(0, self.left.col(0))
        self.up.reverseRow(0)
        self.left.setCol(0, self.down.row(2))
        self.down.setRow(2, tempCol)
        self.down.reverseRow(2)
        Edge.updateEdgeLayers(self, [self.back])
        Corner.updateCornerLayers(self, [self.back])
        solutionSteps.moveList.append(move.backInv)

    def move(self, face, nTimes=1, clockwise=True):
        if clockwise:
            if face==self.up:
                for i in range(nTimes):
                    self.moveUp()
            elif face==self.down:
                for i in range(nTimes):
                    self.moveDown()
            elif face==self.left:
                for i in range(nTimes):
                    self.moveLeft()
            elif face==self.right:
                for i in range(nTimes):
                    self.moveRight()
            elif face==self.front:
                for i in range(nTimes):
                    self.moveFront()
            elif face==self.back:
                for i in range(nTimes):
                    self.moveBack()
        else:
            if face==self.up:
                for i in range(nTimes):
                    self.moveUpInv()
            elif face==self.down:
                for i in range(nTimes):
                    self.moveDownInv()
            elif face==self.left:
                for i in range(nTimes):
                    self.moveLeftInv()
            elif face==self.right:
                for i in range(nTimes):
                    self.moveRightInv()
            elif face==self.front:
                for i in range(nTimes):
                    self.moveFrontInv()
            elif face==self.back:
                for i in range(nTimes):
                    self.moveBackInv()

    def updateColors(self):
        """Update faces wrt colors"""
        for f in self.faceDirectionList:
            color = f.getSquare((1,1)).color
            if color=='white':
                self.white = f
            elif color=='red':
                self.red = f
            elif color=='green':
                self.green = f
            elif color=='orange':
                self.orange = f
            elif color=='blue':
                self.blue = f
            elif color=='yellow':
                self.yellow = f

    def updateSquareFaces(self):
        """Update the 'face' property of all squares"""
        self.up.updateSquareFace()
        self.down.updateSquareFace()
        self.left.updateSquareFace()
        self.right.updateSquareFace()
        self.front.updateSquareFace()
        self.back.updateSquareFace()

    def rotateNS(self):
        """rotate cube from south to north
        (With North, South, East, West on Up face)"""
        logging.debug("Performing rotateNS")
        tempFace = self.up
        self.up = self.front
        self.front = self.down
        self.down = self.back
        self.down.deepReverse()
        self.back = tempFace
        self.back.rotateClockwise()
        self.back.rotateClockwise()
        self.left.rotateCounterClockwise()
        self.right.rotateClockwise()
        self.updateColors()
        self.updateSquareFaces()
        Edge.updateEdgeLayers(self, [self.up, self.back, self.down, self.front])
        Corner.updateCornerLayers(self, [self.up, self.back, self.down, self.front])
        solutionSteps.moveList.append(move.ns)
        
    def rotateEW(self):
        """rotate cube from west to east
        (With North, South, East, West on Up face)"""
        logging.debug("Performing rotateEW")
        tempFace = self.up
        self.up = self.left
        self.up.rotateClockwise()
        self.left = self.down
        self.left.rotateClockwise()
        self.down = self.right
        self.down.rotateClockwise()
        self.right = tempFace
        self.right.rotateClockwise()
        self.front.rotateClockwise()
        self.back.rotateCounterClockwise()
        self.updateColors()
        self.updateSquareFaces()
        Edge.updateEdgeLayers(self, [self.up, self.down, self.left, self.right])
        Corner.updateCornerLayers(self, [self.up, self.down, self.left, self.right])
        solutionSteps.moveList.append(move.ew)

    def spin(self):
        """Spin the cube with up remaining up and down remaining down"""
        logging.debug("Performing Spin")
        tempFace = self.back
        self.back = self.left
        self.left = self.front
        self.front = self.right
        self.right = tempFace
        self.up.rotateClockwise()
        self.down.rotateCounterClockwise()
        self.updateColors()
        self.updateSquareFaces()
        #Layers remain same
        solutionSteps.moveList.append(move.spin)

    def getDirection(self, color):
        """Returns the direction of the 'color' face"""
        for i in self.faceDirectionList:
            if i.getSquare((1,1)).color==color:
                return i
        logging.error("Direction not found for color: %s", color)
        sys.exit(1)

    def orientUp(self, color):
        """Rotate the cube so that 'color' faces up"""
        logging.debug("Orienting the %s color up", color)
        direction = self.getDirection(color)
        if direction==self.up:
            return
        elif direction in [self.down, self.front, self.back]:
            self.rotateNS()
            self.orientUp(color)
        else: #elif direction in [self.left, self.right]:
            self.rotateEW()
            self.orientUp(color)

    def spinToFront(self, color):
        """Spin the cube so that 'color' faces front"""
        logging.debug("Orienting the %s color front", color)
        direction = self.getDirection(color)
        if direction==self.front:
            return
        elif direction in [self.right, self.left, self.back]:
            self.spin()
            self.spinToFront(color)
        else:
           logging.error("Cannot spin side to front")
           sys.exit(1)

    
    def spinToFRD(self, corner):
        """Rotate the cube to bring corner to Front-Right-Down position"""
        cornerFaces = [corner.squares[0].face, corner.squares[1].face, corner.squares[2].face]
        count=0 #to check for infinite loop
        while set(cornerFaces)!=set([self.front, self.right, self.down]):
            self.spin()
            count=count+1
            if count==4:
                logging.error("spinToFrontRightDown() - cannot spin to %s", faceList)
                sys.exit(1)

    def spinToFRU(self, corner):
        """Spin the cube to bring corner to Front-Right-Up position"""
        cornerFaces = [corner.squares[0].face, corner.squares[1].face, corner.squares[2].face]
        count=0 #to check for infinite loop
        while set(cornerFaces)!=set([self.front, self.right, self.up]):
            self.spin()
            count=count+1
            if count==4:
                logging.error("spinToFrontRightDown() - cannot spin to %s", faceList)
                sys.exit(1)

    def spinToFRM(self, edge):
        """Spin the cube to bring edge to Front-Right-Middle position"""
        if edge.layer!=1:
            logging.error("spinToFRM() - edge not in middle layer!")
            sys.exit(1)
        edgeFaces=[edge.squares[0].face, edge.squares[1].face]
        while set(edgeFaces)!=set([self.front, self.right]):
            self.spin()

    def spinToBLU(self, sq1, sq2):
        """Spin the cube to bring squares sq1 and sq2 to Back-Left position on the Up face"""
        if sq1.face!=self.up and sq2.face!=self.up:
            logging.error("spinToBLU() - squares not on Up face!")
            sys.exit(1)
        targetPos=[(0,1),(1,0)]
        squarePos=[sq1.pos, sq2.pos]
        while set(squarePos)!=set(targetPos):
            self.spin()        
            squarePos=[sq1.pos, sq2.pos]

    def spinLineToMidRow(self):
        """Spin 'Line' formation to middle row of up face"""
        if not self.up.hasLine():
            logging.error("spinLineToMidRow() - Line does not exist!")
            sys.exit(1)
        centerColor = self.up.getSquare((1,1)).color
        targetPos=[(1,0),(1,2)]
        colors = [self.up.getSquare(targetPos[0]).color, self.up.getSquare(targetPos[1]).color]
        while set(colors)!=set([centerColor]):
            self.spin()
            colors = [self.up.getSquare(targetPos[0]).color, self.up.getSquare(targetPos[1]).color]

    def spinToBR(self, edgeList):
        """Spin the cube so that specified edges are on Back and Right faces"""
        squareList = []
        for e in edgeList:
            if e.squares[0].face==self.up:
                squareList.append(e.squares[1])
            else:
                squareList.append(e.squares[0])
        count = 0
        while set([squareList[0].face, squareList[1].face])!=set([self.back, self.right]):
            self.spin()
            count=count+1
            if count==4:
                logging.error("spinToBR(): Failed with edges %s", edgeList)
                sys.exit(1)
 
    def printFaces(self):
        """Print the faces of the cube on the commandline"""
        print "up"
        self.up.printFace()
        print "\nright"
        self.right.printFace()
        print "\nfront"
        self.front.printFace()
        print "\nleft"
        self.left.printFace()
        print "\nback"
        self.back.printFace()
        print "\ndown"
        self.down.printFace()

    def printPositions(self):
        """Print the position of each square"""
        #For testing
        print "up"
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.up.face[i][j].pos
        print "\nright"
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.up.face[i][j].pos
        print "\nfront"
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.up.face[i][j].pos
        print "\nleft"
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.up.face[i][j].pos        
        print "\nback"
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.up.face[i][j].pos
        print "\ndown"
        for i in [0,1,2]:
            for j in [0,1,2]:
                print self.up.face[i][j].pos


    def shuffle(self, nMoves=None):
        """Shuffles the cube"""
        if(nMoves == None):
            iterations = random.randrange(25,100)
        else:
            iterations = nMoves
        for i in range(iterations):
            move = random.randrange(12)
            if move == 0:
                self.moveUp()
            elif move == 1:
                self.moveUpInv()
            elif move == 2:
                self.moveDown()
            elif move == 3:
                self.moveDownInv()
            elif move == 4:
                self.moveLeft()
            elif move == 5:
                self.moveLeftInv()
            elif move == 6:
                self.moveRight()
            elif move == 7:
                self.moveRightInv()
            elif move == 8:
                self.moveFront()
            elif move == 9:
                self.moveFrontInv()
            elif move == 10:
                self.moveBack()
            elif move == 11:
                self.moveBackInv()
    
    def testAllMovesOnce(self):
        """Test all moves once"""
        c.moveUp()
        c.moveUp()
        c.moveUp()
        c.moveUp()
    
        c.moveDown()
        c.moveDown()
        c.moveDown()
        c.moveDown()
        
        c.moveLeft()
        c.moveLeft()
        c.moveLeft()
        c.moveLeft()

        c.moveRight()
        c.moveRight()
        c.moveRight()
        c.moveRight()
        
        c.moveFront()
        c.moveFront()
        c.moveFront()
        c.moveFront()
        
        c.moveBack()
        c.moveBack()
        c.moveBack()
        c.moveBack()
        
        c.moveUpInv()
        c.moveUpInv()
        c.moveUpInv()
        c.moveUpInv()
        
        c.moveDownInv()
        c.moveDownInv()
        c.moveDownInv()
        c.moveDownInv()
        
        c.moveLeftInv()
        c.moveLeftInv()
        c.moveLeftInv()
        c.moveLeftInv()

        c.moveRightInv()
        c.moveRightInv()
        c.moveRightInv()
        c.moveRightInv()
        
        c.moveFrontInv()
        c.moveFrontInv()
        c.moveFrontInv()
        c.moveFrontInv()
        
        c.moveBackInv()
        c.moveBackInv()
        c.moveBackInv()
        c.moveBackInv()


class Solver:
    """Methods for solving the cube"""

    def __init__(self, cube):
        self.cube = cube
    
    def algo_R_D_RD(self):
        """Algo: R' D' R D"""
        self.cube.moveRightInv()
        self.cube.moveDownInv()
        self.cube.moveRight()
        self.cube.moveDown()

    def algo_URU_L_UR_U_L(self):
        """Algo: U R U' L' U R' U' L"""
        self.cube.moveUp()
        self.cube.moveRight()
        self.cube.moveUpInv()
        self.cube.moveLeftInv()
        self.cube.moveUp()
        self.cube.moveRightInv()
        self.cube.moveUpInv()
        self.cube.moveLeft()

    def algo_FRUR_U_F_(self):
        """algo: F R U R' U' F'"""
        self.cube.moveFront()
        self.cube.moveRight()
        self.cube.moveUp()
        self.cube.moveRightInv()
        self.cube.moveUpInv()
        self.cube.moveFrontInv()

    def algo_RUR_UR2UR_(self):
        """algo: R U R' U R 2U R'"""
        self.cube.moveRight()
        self.cube.moveUp()
        self.cube.moveRightInv()
        self.cube.moveUp()
        self.cube.moveRight()
        self.cube.moveUp()
        self.cube.moveUp()
        self.cube.moveRightInv()

    def getEdge(self, layerList, color):
        """Returns an edge containing 'color' from the specified layers"""
        for edge in self.cube.edgeList:
            if edge.layer in layerList:
                for square in edge.squares:
                    if square.color == color:
                        return edge
        return None

    def getEdgeSans(self, color, layerList):
        """Returns an edge without 'color' from the specified layers"""
        for edge in self.cube.edgeList:
            if edge.layer in layerList:
                if edge.squares[0].color!=color and edge.squares[1].color!=color:
                    return edge
        return None

    def getTopSolvedEdges(self):
        """Get the solved edges from the top layer"""
        edgeList = []
        for e in Edge.edgeLocations:
            edge = self.cube.up.getSquare(e).edge
            if edge.isOriented():
                edgeList.append(edge)
        return edgeList

    def getCorner(self, layerList, color):
        """look for corners containing specifed color in given list"""
        for corner in self.cube.cornerList:
            if corner.layer in layerList:
                for square in corner.squares:
                    if square.color==color:
                        return corner
        return None

    def getCorners(self, face):
        """Return all the corners of a face"""
        cornerList = []
        for c in Corner.cornerLocations:
            cornerList.append(face.getSquare(c).corner)
        return cornerList

    def orientEdge(self, edge, color):
        """Orients an aligned edge to its proper face (for first cross)"""
        if not edge.isOriented():
            self.cube.orientUp(color)
            if edge.squares[0].color==color:
                otherColor = edge.squares[1].color
            else:
                otherColor = edge.squares[0].color
            self.cube.spinToFront(otherColor)
            #Algo: F' U L' U'
            self.cube.moveFrontInv()
            self.cube.moveUp()
            self.cube.moveLeftInv()
            self.cube.moveUp()

    def orientCorner(self, corner):
        """Orient the corner in its proper position"""
        if corner.layer==2:
            self.cube.spinToFRD(corner)
            while not corner.isOriented():
                self.algo_R_D_RD()
        elif corner.layer==0:
            self.cube.spinToFRU(corner)
            self.algo_R_D_RD() #will move the corner to bottom layer and next iteration will take care of it

    def hasCross(self, color):
        """Determines if the up face has a cross(but may not be aligned)"""
        if self.cube.up.getSquare((1,1)).color!=color:
            logging.warning("hasCross(): Argument does not match center color")
            return False
        for e in Edge.edgeLocations:
            if self.cube.up.getSquare(e).color!=color:
                return False
        return True        

    def crossIsSolved(self):
        """Determines whether the cross is solved"""
        #face = self.cube.getDirection(color)
        face = self.cube.up #always
        for e in Edge.edgeLocations:
            edge = face.getSquare(e).edge
            if not edge.isOriented():
                return False
        return True

    def topLayerIsSolved(self):
        """Checks if the top layer is solved"""
        centerColor = self.cube.up.getSquare((1,1)).color
        for r in [0,1,2]:
            for c in [0,1,2]:
                if self.cube.up.getSquare((r,c)).color!=centerColor:
                    return False
        for face in [self.cube.front, self.cube.left, self.cube.right, self.cube.back]:
            centerColor = face.getSquare((1,1)).color
            for c in [0,1,2]:
                if face.getSquare((0,c)).color!=centerColor:
                    return False
        return True

    def middleLayerIsSolved(self):
        """Checks if the middle layer is solved"""
        for face in self.cube.faceList:
            if face==self.cube.up or face==self.cube.down:
                pass
            else:
                centerColor = face.getSquare((1,1)).color
                for col in [0,1,2]:
                    if face.getSquare((1,col)).color!=centerColor:
                        return False
        return True                    


    def alignedEdgesAreOpp(self, edgeList):
        """Checks if the two solved edges are adjacent in the top layer"""
        faceList = []
        for e in edgeList:
            if e.squares[0].face==self.cube.up:
                faceList.append(e.squares[1].face)
            else:
                faceList.append(e.squares[0].face)
        oppFaces = [ set([self.cube.front, self.cube.back]), set([self.cube.right, self.cube.left]) ]
        if set(faceList) in oppFaces:
            return True
        else:
            return False

    def numSolvedEdges(self, layerList):
        """Returns the number of solved edges in the layer(s)"""
        edgeCount = 0
        for edge in self.cube.edgeList:
            if edge.layer in layerList:
                if edge.isOriented():
                    edgeCount = edgeCount+1
        return edgeCount

    def numPositionedCorners(self, layerList):
        """Returns the number of positioned corners(but may not be oriented) in specified layers"""
        count = 0
        for c in self.cube.cornerList:
            if c.layer in layerList:
                if c.isInPlace():
                    count = count + 1
        return count
    
    def solveFirstCross(self, color):
        """Solve the cross of the specified color"""
        logging.debug("Solving cross")
        while not self.crossIsSolved():
            edge = self.getEdge([2], color)
            while edge!=None:
                edge.align(self.cube, color)
                edge.bringToTop(self.cube)
                self.orientEdge(edge, color)
                edge = self.getEdge([2], color)
            edge = self.getEdge([1], color)
            if edge!=None:
                edge.bringToBottom(self.cube, color)
            edge = self.getEdge([2,1], color)
            if edge==None:
                for e in Edge.edgeLocations:
                    edge = self.cube.up.getSquare(e).edge
                    if not edge.isOriented():
                        edge.bringToBottom(self.cube, color)
    
    def solveFirstCorners(self, color):
        """Solve the corners of the first layer"""
        logging.debug("Solving First Corners")
        while not self.topLayerIsSolved():
            corner = self.getCorner([2], color)
            while corner!=None:
                corner.alignUnder(color, self.cube)
                self.orientCorner(corner)
                corner = self.getCorner([2], color)
            for c in Corner.cornerLocations:
                corner = self.cube.up.getSquare(c).corner
                if not corner.isOriented():
                    self.orientCorner(corner)
                    break
                
    def solveMiddleLayer(self, color):
        """Solve the middle layer of the cube"""
        logging.debug("Solving middle layer")
        while not self.middleLayerIsSolved():
            edge = self.getEdgeSans(color, [0])
            while edge!=None:
                if edge.squares[0].face==self.cube.up:
                    ignoredColor = edge.squares[0].color
                    alignedColor = edge.squares[1].color
                else:
                    ignoredColor = edge.squares[1].color
                    alignedColor = edge.squares[0].color
                edge.align(self.cube, ignoredColor)
                self.cube.spinToFront(alignedColor)
                if ignoredColor==self.cube.left.getSquare((1,1)).color:
                    #algo: U' L' U L U F U' F'
                    self.cube.moveUpInv()
                    self.cube.moveLeftInv()
                    self.cube.moveUp()
                    self.cube.moveLeft()
                    self.cube.moveUp()
                    self.cube.moveFront()
                    self.cube.moveUpInv()
                    self.cube.moveFrontInv()
                elif ignoredColor==self.cube.right.getSquare((1,1)).color:
                    #algo: U R U' R' U' F' U F
                    self.cube.moveUp()
                    self.cube.moveRight()
                    self.cube.moveUpInv()
                    self.cube.moveRightInv()
                    self.cube.moveUpInv()
                    self.cube.moveFrontInv()
                    self.cube.moveUp()
                    self.cube.moveFront()
                else:
                    logging.error("solveMiddleLayer() - edge (%s %s) shouldn't exist!", alignedColor, ignoredColor)
                    sys.exit(1)
                edge = self.getEdgeSans(color, [0])
            for edge in self.cube.edgeList:
                if edge.layer==1 and edge.isOriented()==False:
                    self.cube.spinToFRM(edge)
                    #algo: U R U' R' U' F' U F
                    self.cube.moveUp()
                    self.cube.moveRight()
                    self.cube.moveUpInv()
                    self.cube.moveRightInv()
                    self.cube.moveUpInv()
                    self.cube.moveFrontInv()
                    self.cube.moveUp()
                    self.cube.moveFront()
                    break

    def makeL(self, color):
        """Form an L shape with the specified color"""
        #Possible L configurations:
        # (0,1)-(1,0)
        # (0,1)-(1,2)
        # (2,1)-(1,0)
        # (2,1)-(2,2)
        for pos1 in [(0,1), (2,1)]:
            sq1 = self.cube.up.getSquare(pos1)
            if sq1.color==color:
                for pos2 in [(1,0), (1,2)]:
                    sq2 = self.cube.up.getSquare(pos2)
                    if sq2.color==color:
                        self.cube.spinToBLU(sq1,sq2)
                        return
        self.algo_FRUR_U_F_()
        self.makeL(color)

    def solveSecondCross(self, color):
        """Get the cross after 2 layers are already solved"""
        logging.debug("Solving second cross")
        if not self.hasCross(color):
            if not self.cube.up.hasLine():
                self.makeL(color)
                self.algo_FRUR_U_F_()
            self.cube.spinLineToMidRow()
            self.algo_FRUR_U_F_()

    def completeSecondCross(self, color):
        """Complete the second cross by aligning/orienting edges"""
        moveCount = 0
        while self.numSolvedEdges([0])<2:
            self.cube.moveUp()
            moveCount = moveCount+1
            if moveCount==4:
                self.algo_RUR_UR2UR_()
        if self.numSolvedEdges([0])==2:
            #getting the solved edges->
            edgeList = self.getTopSolvedEdges()
            if len(edgeList)==1:
                logging.error("completeSecondCross(): Only one aligned edge! Something went wrong!")
                sys.exit(1)
            if self.alignedEdgesAreOpp(edgeList):
                #bring an aligned edge to front face->
                if edgeList[0].squares[0].color==color:
                    adjColor = edgeList[0].squares[1].color
                else:
                    adjColor = edgeList[0].squares[0].color
                self.cube.spinToFront(adjColor)
                #making them adjacent->
                self.algo_RUR_UR2UR_()
                edgeList = self.getTopSolvedEdges()
            self.cube.spinToBR(edgeList)
            self.algo_RUR_UR2UR_()
        moveCount = 0
        while not self.crossIsSolved():
            self.cube.moveUp()
            moveCount = moveCount+1
            if moveCount==3:
                logging.error("completeSecondCross(): Failed to solve!")
                sys.exit(1)         

    def positionSecondCorners(self):
        """Position the corners after 2 layers and the cross are solved"""
        if self.numPositionedCorners([0])==0:
            self.algo_URU_L_UR_U_L()
        while self.numPositionedCorners([0])<4:
            #get a corner in proper position->
            cornerList = self.getCorners(self.cube.up)
            for corner in cornerList:
                if corner.isInPlace():
                    break
            self.cube.spinToFRU(corner)
            #apply algo->
            self.algo_URU_L_UR_U_L()       

    def orientSecondCorners(self, color):
        """Orient the up-face corners correctly"""
        cornerList = self.getCorners(self.cube.up)
        for corner in cornerList:
            if corner.isInPlace():
                break
        self.cube.spinToFRU(corner)
        while not self.cube.up.getSquare((2,2)).color==color:
            self.algo_R_D_RD()
        for i in range(4):
            self.cube.moveUp()
            while not self.cube.up.getSquare((2,2)).color==color:
                self.algo_R_D_RD()
        for i in range(4):
            if not self.topLayerIsSolved():
                self.cube.moveUp()
                break

    def danBrown(self):
        """Solve the cube using the 'layer-by-layer' approach"""
        solutionSteps.clear()
        color='white' #TODO: Find best cross to solve 
        self.cube.orientUp(color) 
        self.cube.printFaces()
        self.solveFirstCross(color)
        self.cube.printFaces()
        self.solveFirstCorners(color)
        color = self.cube.down.getSquare((1,1)).color
        self.cube.orientUp(color)
        self.cube.printFaces()
        self.solveMiddleLayer(color)
        self.cube.printFaces()
        self.solveSecondCross(color)
        self.completeSecondCross(color)
        self.positionSecondCorners()
        self.orientSecondCorners(color)

    def getSolutionSteps(self):
        steps = solutionSteps.moveList[:]
        return steps
        

if __name__ == "__main__":
    c = Cube()
    c.printFaces()
    c.shuffle()
    c.printFaces()
    s = Solver(c)
    s.danBrown()
    print "Final:"
    c.printFaces()
    
    moves = s.getSolutionSteps()
    print "---before optimize---"
    print moves
    print "Total: ", len(moves)
    moves = solsteps.SolutionSteps.basicOptimize(moves)    
    print "---after optimize---"
    print moves
    print "Total: ", len(moves)
    
