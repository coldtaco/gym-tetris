import numpy as np
import copy
import traceback
import sys
import pandas as pd
import curses
import gym
#TODO implement changes record
class TetrisSimple(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(TetrisSimple, self).__init__()
        self.bag = self.newBag()
        board = [0 for x in range(10)]
        board = [list(board) for x in range(20)]
        self.action_space = gym.spaces.MultiDiscrete([10,4])
        self.observation_space = gym.spaces.Box(0,2,[20,10])
        self.board = board
        self.piece = self.bag.pop()
        self.rotation = 0
        self.marker = [-2,5]
        self.hold = None
        self.fall = False
        self.touched  = 0
        self.cleared = 0
        self.running = True
        self.coords = self.orientation()
        self.score = 0
        self.b2b = False
        self.held = False
        self.hiddenScore = 0
        self.pieces = 0
        self.lastHeight = 0

    def step(self, action):
        self.take_action(action)
        reward = self.score
        ob = self.board
        episode_over = not self.running
        return ob, reward, episode_over, {}

    def reset(self):
        board = [0 for x in range(10)]
        board = [list(board) for x in range(20)]
        self.board = board
        x = np.array(self.board)
        assert len(x.shape) == 2
        self.piece = self.bag.pop()
        self.rotation = 0
        self.marker = [-2,5]
        self.hold = None
        self.fall = False
        self.touched  = 0
        self.cleared = 0
        self.running = True
        self.coords = self.orientation()
        self.score = 0
        self.b2b = False
        self.held = False
        self.hiddenScore = 0
        self.pieces = 0
        self.lastHeight = 0
        return x

    def render(self, mode='human', close=False):
        self.drawBoard()
        pass

    def take_action(self, action):
        self.marker[1], self.rotation = action[0]
        self.hardDrop()
        self.clear()
        self.coords = self.orientation()
        self.setPiece()

    def dBoard(self,crash):
        tempBoard = copy.deepcopy(self.board)
        string = ""
        for y in tempBoard:
            for x in y:
                if x == 2:
                    string += "#"
                    print('#',end='')
                elif x == 1:
                    string += "0"
                    print('0',end='')
                else:
                    string += " "
                    print(" ",end='')
            string += '\n'
            print("\n",end='')
        crash.write(string)
        crash.write(str(self.coords)+'\n')
        crash.write(str(self.marker)+'\n')
        crash.write(str(self.piece)+'\n')
        crash.write(str(self.rotation)+'\n')

    def get_reward(self):
        """ Reward is given for XY. """
        return self.score

    def seed(self):
        return

    def drawBoard(self,prin = True):
        tempBoard = copy.deepcopy(self.board)
        coords = self.orientation() 
        for y,x in coords:
            if y < 0:
                continue
            if tempBoard[y][x] == 2:
                continue
            tempBoard[y][x] = 1
        if prin:
            for y in tempBoard:
                for x in y:
                    if x == 2:
                        print('#',end='')
                    elif x == 1:
                        print('0',end='')
                    else:
                        print(" ",end='')
                print('\n',end='')
        else:
            strings = []
            for y in tempBoard:
                string = ""
                for x in y:
                    if x == 2:
                        string +='■'
                    elif x == 1:
                        string +='#'
                    else:
                        string +=' '
                    string +=' '
                strings.append(string)
            strings.append(f"Lines cleared : {self.cleared}\n")
            strings.append(f"Score : {self.score}\n")
            return strings

    def hardDrop(self):
        orientation = self.orientation()
        lowest = {}
        lowestPosition = -2
        for y,x in orientation:
            assert y <= 19, "y value was " + str(y) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
            assert x >= 0, "x value was " + str(x) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
            assert x <= 9, "x value was " + str(x) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
            if x in lowest:
                lowest[x] = y - self.marker[0] if lowest[x] < y - self.marker[0] else lowest[x]
            else:
                lowest[x] = y - self.marker[0]
            lowestPosition = y if lowestPosition < y else lowestPosition
        lowestPosition -= self.marker[0]
        keys = list(lowest.keys())
        y_ = self.marker[0]
        while y_ < 0:
            for y in lowest.values():
                if y < 0:
                    for x in lowest:
                        lowest[x] += 1
            y_ += 1
        for y in range(len(self.board)+2):
            if lowest[x] + y < 0:
                continue
            for x in keys:
                assert y >= 0, "y value was " + str(y) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
                assert y <= 19, "y value was " + str(y) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
                assert x >= 0, "x value was " + str(x) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
                assert x <= 9, "x value was " + str(x) + " lowest[x] + y = " + str(lowest[x] + y) + " " + str(orientation)
                if self.board[lowest[x]+y][x] == 2:
                    self.score += (y - self.marker[0] - 1)*2
                    self.marker[0] = y - 1
                    return
                if lowest[x]+y >= 19 :
                    self.score += (19 - lowestPosition- self.marker[0])*2
                    self.marker[0] = 19 - lowestPosition
                    return

    def orientation(self):#return list of tuples of coordinates of tetrimino when drawn
        x = self.marker[0]
        y = self.marker[1]
        piece = self.piece
        if piece == 0:
            if self.rotation % 4 == 0:
                return ((x-1,y),(x,y),(x+1,y),(x+2,y))
            elif self.rotation % 4 == 1:
                return ((x,y-1),(x,y),(x,y+1),(x,y+2))
            elif self.rotation % 4 == 2:
                return ((x-2,y),(x-1,y),(x,y),(x+1,y))
            elif self.rotation % 4 == 3:
                return ((x,y-2),(x,y-1),(x,y),(x,y+1))
        elif piece == 1:
            return ((x,y),(x,y+1),(x+1,y),(x+1,y+1))
        elif piece == 2:
            if self.rotation % 4 == 0:
                return ((x,y+1),(x,y),(x,y-1),(x-1,y))
            elif self.rotation % 4 == 1:
                return ((x-1,y),(x,y),(x+1,y),(x,y+1))
            elif self.rotation % 4 == 2:
                return ((x,y+1),(x,y),(x,y-1),(x+1,y))
            elif self.rotation % 4 == 3:
                return ((x-1,y),(x,y),(x+1,y),(x,y-1))
        elif piece == 3:
            if self.rotation % 4 == 0:
                return ((x-1,y+1),(x,y+1),(x,y),(x,y-1))
            elif self.rotation % 4 == 1:
                return ((x-1,y),(x,y),(x+1,y),(x+1,y+1))
            elif self.rotation % 4 == 2:
                return ((x+1,y-1),(x,y+1),(x,y),(x,y-1))
            elif self.rotation % 4 == 3:
                return ((x-1,y),(x,y),(x+1,y),(x-1,y-1))
        elif piece == 4:
            if self.rotation % 4 == 0:
                return ((x-1,y-1),(x,y+1),(x,y),(x,y-1))
            elif self.rotation % 4 == 1:
                return ((x-1,y),(x,y),(x+1,y),(x-1,y+1))
            elif self.rotation % 4 == 2:
                return ((x+1,y+1),(x,y+1),(x,y),(x,y-1))
            elif self.rotation % 4 == 3:
                return ((x-1,y),(x,y),(x+1,y),(x+1,y-1))
        elif piece == 5:
            #s
            if self.rotation % 4 == 0:
                return ((x,y-1),(x,y),(x+1,y),(x+1,y+1))
            elif self.rotation % 4 == 1:
                return ((x-1,y+1),(x+1,y),(x,y),(x,y+1))
            elif self.rotation % 4 == 2:
                return ((x,y),(x-1,y),(x,y+1),(x-1,y-1))
            elif self.rotation % 4 == 3:
                return ((x+1,y-1),(x,y-1),(x-1,y),(x,y))
        elif piece == 6:
            #z
            if self.rotation % 4 == 0:
                return ((x+1,y-1),(x+1,y),(x,y),(x,y+1))
            elif self.rotation % 4 == 1:
                return ((x-1,y),(x,y),(x,y+1),(x+1,y+1))
            elif self.rotation % 4 == 2:
                return ((x,y-1),(x,y),(x-1,y),(x-1,y+1))
            elif self.rotation % 4 == 3:
                return ((x-1,y-1),(x,y-1),(x,y),(x+1,y))

    def setPiece(self):#sets tetrimino in place and resets some info used for tracking it
        self.pieces += 1
        self.lastHeight = self.marker[0]
        for y,x in self.coords:
            if y < 0:
                self.endGame()
                return
            assert y >= 0, "y value was " + str(y)
            assert y <= 19, "y value was " + str(y)
            assert x >= 0, "x value was " + str(x)
            assert x <= 9, "x value was " + str(x)
            self.board[y][x] = 2
        self.clear()
        if len(self.bag) < 5:
            self.bag += self.newBag()
        self.piece = self.bag.pop()
        self.rotation = 0
        self.touched = 0
        self.marker = [-2,5]
        self.held = False
        self.coords = self.orientation()
        if self.overlapCheck():
            self.endGame()
    
    def endGame(self):
        self.running = False

    def overlapCheck(self):
    #checks if there is overlap (does not correct). Used for stopping certain moves
        for i,z in enumerate(self.orientation()):
            y,x = z
            if x < 0:
                return True
            elif x > 9:
                return True
            if y < 0:
                continue
            if y > 19:
                return True
            if self.board[y][x] == 2:
                return True
        return False

    def newBag(self):#creatse a new bag of tetriminos
        bag = list(range(7))
        bag = bag*2
        np.random.shuffle(bag)
        return bag
            
    def clear(self):#clears lines
        linesCleared = 0
        tempBoard = []
        for i,x in enumerate(list(reversed(self.board))):
            if 0 not in x:
                linesCleared += 1
            else:
                tempBoard.insert(0,x)
        for i in range(len(self.board) - len(tempBoard)):
            tempBoard.insert(0,list([0,0,0,0,0,0,0,0,0,0]))
        self.b2b = False if linesCleared == 0 else True
        if linesCleared == 1:
            self.score += 150 if self.b2b else 100
        elif linesCleared == 2:
            self.score += 450 if self.b2b else 300
        elif linesCleared == 3:
            self.score += 750 if self.b2b else 500
        elif linesCleared == 4:
            self.score += 1200 if self.b2b else 800
        self.cleared += linesCleared
        self.board = tempBoard