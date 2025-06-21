# https://neat-python.readthedocs.io/en/latest/xor_example.html
import neat.genes
from dilema.game import Game
import pygame
import neat
import os
import time
import pickle

RED = (200, 0, 0)
GREEN = (0, 200, 0)

matrix = [
    [[1,1],[-1,2]],
    [[2,-1],[0,0]]
]

meanNumRounds, std, minNumRounds, maxNumRounds = None, None, None, None
lastRoundChance = 0.05
drawTraining = False
choiceStrenghtMultiplier = 1




class DilemaGame:
    def __init__(self, matrix, lastRoundChance=None,  meanNumRounds=None, std=None, minNumRounds=None, maxNumRounds=None):
        if lastRoundChance != None:
            self.game = Game(matrix, lastRoundChance)
        else:
            self.game = Game(matrix, meanNumRounds, std, minNumRounds, maxNumRounds)
        self.win = self.game.getWindow()


    def test_ai(self, net):
        """
        Test the AI against a human player by passing a NEAT neural network
        """
        self.reset()
        run = True
        clicked = False

        win = self.game.getWindow()

        pygame.draw.rect(win, RED, defectRect)
        pygame.draw.rect(win, GREEN, coopRect)
        pygame.display.update()

        while run:

            choices = self.game.getChoices()
            cooperations = self.game.getTotalCooperations()
            defects = self.game.getTotalDefects()
            totalChoices = len(choices[0]) - 1

            output = net.activate((
                choices[1][totalChoices] * choiceStrenghtMultiplier, 
                choices[1][totalChoices - 1] * choiceStrenghtMultiplier,
                choices[1][totalChoices - 2] * choiceStrenghtMultiplier, 
                cooperations[1],
                defects[1])
            )
            
            agentChoice = output.index(max(output))

            deciding = True
            
            
            
            while deciding:
                if not clicked and pygame.mouse.get_pressed()[0]:

                    if defectRect.collidepoint(pygame.mouse.get_pos()):
                        #print("Player choose to defect")
                        playerChoice = 1
                        clicked = True
                        deciding = False
                    elif coopRect.collidepoint(pygame.mouse.get_pos()):
                        #print("Player choose to cooperate")
                        playerChoice = 0
                        clicked = True
                        deciding = False


                if not pygame.mouse.get_pressed()[0]:
                    clicked = False
            

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
            #print("Player choice: ", playerChoice)
            #print("Agent choice: ", agentChoice)
            self.game.runRound(agentChoice, playerChoice, True, False)


            if self.game.gameOver():
                #print("Game over")
                run = False



   



    def train_ai(self, genome1, genome2, config, draw=False):
        """
        Train the AI by passing two NEAT neural networks and the NEAT config object.
        These AI's will play against eachother to determine their fitness.
        """
        #print("Training AI...")
        self.reset()
        run = True

        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)
        self.genome1 = genome1
        self.genome2 = genome2

        score1 = 0
        score2 = 0
        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            choices = self.game.getChoices()
            cooperations = self.game.getTotalCooperations()
            defects = self.game.getTotalDefects()
            
            totalChoices = len(choices[0]) - 1

            output1 = net1.activate((
                choices[1][totalChoices] * choiceStrenghtMultiplier, 
                choices[1][totalChoices - 1] * choiceStrenghtMultiplier, 
                choices[1][totalChoices - 2] * choiceStrenghtMultiplier,
                cooperations[1],
                defects[1]
            ))
            output2 = net2.activate((
                choices[0][totalChoices] * choiceStrenghtMultiplier, 
                choices[0][totalChoices - 1] * choiceStrenghtMultiplier, 
                choices[0][totalChoices - 2] * choiceStrenghtMultiplier,
                cooperations[0],
                defects[0]
            ))

            choice1 = output1.index(max(output1))
            choice2 = output2.index(max(output2))
            #print("AI choice 1: ", choice1)
            #print("AI choice 2: ", choice2)

            scores = self.game.runRound(choice1, choice2, drawTraining)
            score1 += scores[0]
            score2 += scores[1]


            #pygame.display.update()
            #pygame.draw.circle(win, (0, 0, 0), (width/2, height/2), 100)

            if self.game.gameOver():
                numRounds = self.game.numRounds
                self.calculate_fitness(score1 / numRounds, score2 / numRounds)
                break

        return False
    scores = []
    improvementOffset = 0

    def calculate_fitness(self, score1, score2):
        #print("calculating fitness...")
        
        self.genome1.fitness += score1
        self.genome2.fitness += score2
        self.scores.append(score1)
        self.scores.append(score2)

    def reset(self):
        """
        Reset the game state
        """
        self.game.reset()


dilema = DilemaGame(matrix, lastRoundChance)

#win = pygame.display.set_mode((width, height))

rectWidth, rectHeight = 200, 50
rectSideDistance = 100
rectBottomDistance = 50
win = dilema.game.getWindow()
winWidth, winHeight = win.get_width(), win.get_height()

defectRect = pygame.Rect(winWidth - rectSideDistance - rectWidth, winHeight - rectBottomDistance - rectHeight, rectWidth, rectHeight)
coopRect = pygame.Rect(rectSideDistance, winHeight - rectBottomDistance - rectHeight, rectWidth, rectHeight)


def eval_genomes(genomes, config):
    """
    Run each genome against eachother one time to determine the fitness.
    """
    #print("Evaluating genomes...")
    #width, height = 700, 500
    #win = pygame.display.set_mode((width, height))
    #pygame.display.set_caption("Pong")

    
    dilema.game.setNumRounds()
    for i, (genome_id1, genome1) in enumerate(genomes):
        print(round(i/len(genomes) * 100), end=" ")
        genome1.fitness = 0
        for genome_id2, genome2 in genomes[min(i+1, len(genomes) - 1):]:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
            #dilema = DilemaGame(matrix, meanNumRounds, std, minNumRounds, maxNumRounds)

            force_quit = dilema.train_ai(genome1, genome2, config, draw=False)


            if force_quit:
                return True
  
    dilema.scores = []

    for genome_id, genome in genomes:
        genome.fitness -= dilema.improvementOffset
            

def add_connection(genome, inNode, outNode, weight):
    """
    Add a connection to the genome.
    """
    key = (inNode, outNode)

    connection = neat.genes.DefaultConnectionGene(key)
    connection.weight = weight
    connection.enabled = True
    
    genome.connections[key] = connection
        
def run_neat(config):
    
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-99')
    
    #p = neat.Population(config)
    #for i in range(1, 51):
    #    genome = p.population[i]
    #    add_connection(genome, 0, 1, 10)
        
        #genome.nodes[0].bias = -1

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(100))

    winner = p.run(eval_genomes, 1)
    with open("best.pickle", "wb") as f:
        print("Saving best genome...")
        pickle.dump(winner, f)


def test_best_network(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    #dilema = DilemaGame(matrix, meanNumRounds, std, minNumRounds, maxNumRounds)
    dilema.test_ai(winner_net)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet, 
        neat.DefaultStagnation,
        config_path
    )

    run_neat(config)
    test_best_network(config)


