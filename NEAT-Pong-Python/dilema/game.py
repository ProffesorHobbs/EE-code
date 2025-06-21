import random
import math
import pygame

winHeight = 1000
winWidth = 1600


RED = (200, 0, 0)
GREEN = (0, 200, 0)

sideDistance = 5
circleCount = 60

cicleDistance = winWidth / circleCount 

class Game:
    
    

    def __init__(self, matrix, lastRoundChance=None, roundLength=None):
        self.window = pygame.display.set_mode((winWidth, winHeight))
        pygame.display.set_caption("Repeated Prisoner's Dilemma")

        self.matrix = matrix

        

        

        self.currentRound = 0
        

        self.p1_score = 0
        self.p2_score = 0

        self.choices = [[0,0,0],[0,0,0]]

        self.defects = [0,0]
        self.cooperations = [0,0]
        if roundLength == None:
            self.lastRoundChance = lastRoundChance
        else:
            self.roundLength = roundLength

        
    def getWindow(self):
        """
        Returns the window of the game
        """
        return self.window

    def getTotalCooperations(self):
        """
        Returns the total number of cooperations for both players
        """
        return self.cooperations
    

    def getTotalDefects(self):
        """
        Returns the total number of defects for both players
        """
        return self.defects
    

    def runRound(self, p1Choice, p2Choice, drawRound=False, cleanCanvas=True):
        """
        Runs a round of the game and returns the score for both players
        """
        #print("Round Ran")
        self.currentRound += 1

        self.choices[0].append(p1Choice)
        self.choices[1].append(p2Choice)
        
        if(p1Choice == 0):
            self.cooperations[0] += 1
        else:
            self.defects[0] += 1

        if(p2Choice == 0):
            self.cooperations[1] += 1
        else: 
            self.defects[1] += 1

        if drawRound:
            self.drawRound(cleanCanvas)
        #print("Total Choices: ", len(self.choices[0]))
        return self.matrix[p1Choice][p2Choice]
    
    def gameOver(self):
        """
        Returns True if the game is over, False otherwise
        """
        
        #print("Current round: ", self.numRounds)


        #if gameOver:
            #self.reset()
        return self.currentRound >= self.numRounds
    def setNumRounds(self, numRounds=None):
        """
        Sets the number of rounds in the game
        """
        if numRounds is None:
            epsilon = 1e-10
            rand = random.uniform(epsilon, 1 - epsilon)
            self.numRounds = math.floor(math.log(rand, 1 - self.lastRoundChance)) + 1
        else:
            self.numRounds = numRounds
        print("Number of rounds: ", self.numRounds)
        print("Random Number: ", rand)

    def getCurrentRound(self):
        return self.currentRound

    def reset(self):
        """
        Resets the game state
        """
        #print("Resetting game")
        self.currentRound = 0

        self.p1_score = 0
        self.p2_score = 0

        self.choices = [[0,0,0],[0,0,0]]

        self.defects = [0,0]
        self.cooperations = [0,0]
        


    def getChoices(self):
        """
        Returns the choices of both players
        """
        choices = [[],[]]
        for i in range(2):
            for choice in self.choices[i]:
                if choice == 0:
                    choice = -1
                choices[i].append(choice)
        return choices

    

    def drawRound(self, cleanCanvas=True):
        """
        Draws the current round
        """
        #print("Drawing round")
        
        numChoices = len(self.choices[0])
        radius = 5
        j = 0
        
        for i in range(max(3, numChoices - circleCount), numChoices, + 1):
            #print("Drawing circle")
            
            

            color = RED if self.choices[1][i] == 1 else GREEN
            
            pygame.draw.circle(self.window, color, (sideDistance + j * cicleDistance, winHeight / 4), radius)
            #print(sideDistance + j * cicleDistance, winHeight / 4)

            color = RED if self.choices[0][i] == 1 else GREEN

            pygame.draw.circle(self.window, color, (sideDistance + j * cicleDistance, winHeight * (3/4)), radius)

            j += 1

            
        
        pygame.display.update()
        if cleanCanvas:
            self.window.fill((0, 0, 0))
        


        

        

    

        


