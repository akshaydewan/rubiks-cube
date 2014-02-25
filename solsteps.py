#!/usr/bin/env python

import sys
import copy
import random
import logging
import pdb

logging.basicConfig(level=logging.DEBUG)

class SolutionSteps:
    """Contains the steps for the solution"""
    moveList = []

    def clear(self):
        self.moveList = []

    @staticmethod
    def basicOptimize(moves):
        """Perform simple optimization of moves"""
        optimizedMoves = []
        totalMoves = len(moves)
        i = 0
        while i < totalMoves:
            optimized = False
            if (i<totalMoves - 2) and (moves[i] == moves[i+1] == moves[i+2]):
                if moves[i] == Move.up:
                    optimized = True
                    optimizedMoves.append(Move.upInv)
                elif moves[i] == Move.upInv:
                    optimized = True
                    opimizedMoves.append(Move.up)
                elif moves[i] == Move.down:
                    optimized = True
                    optimizedMoves.append(Move.downInv)
                elif moves[i] == Move.downInv:
                    optimized = True
                    opimizedMoves.append(Move.down)
                elif moves[i] == Move.left:
                    optimized = True
                    optimizedMoves.append(Move.leftInv)
                elif moves[i] == Move.leftInv:
                    optimized = True
                    opimizedMoves.append(Move.left)
                elif moves[i] == Move.right:
                    optimized = True
                    optimizedMoves.append(Move.rightInv)
                elif moves[i] == Move.rightInv:
                    optimized = True
                    opimizedMoves.append(Move.right)
                elif moves[i] == Move.front:
                    optimized = True
                    optimizedMoves.append(Move.frontInv)
                elif moves[i] == Move.frontInv:
                    optimized = True
                    opimizedMoves.append(Move.front)
                elif moves[i] == Move.back:
                    optimized = True
                    optimizedMoves.append(Move.backInv)
                elif moves[i] == Move.backInv:
                    optimized = True
                    opimizedMoves.append(Move.back)
            if not optimized:
                optimizedMoves.append(moves[i])
            else:
                i += 2
            i += 1
        return optimizedMoves                                            
    
class Move:
    (up, upInv, down, downInv, left, leftInv, right, rightInv, front, frontInv, back, backInv, ns, ew, spin) = range(15)

    @staticmethod
    def getRandomMove():
        move = random.randrange(15)
        return move

if __name__ == "__main__":
    # Test BasicOptimize function
    moveList = [Move.upInv, Move.down, Move.downInv, Move.left, Move.leftInv, Move.right, Move.rightInv, Move.front, Move.frontInv, Move.back, Move.backInv, Move.ns, Move.ew, Move.spin, Move.up, Move.up, Move.up]
    print "===Before Optimizing==="
    print moveList
    moveList = SolutionSteps.basicOptimize(moveList)
    print "===After Optimizing==="
    print moveList
