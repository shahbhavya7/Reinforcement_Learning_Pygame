import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
# from model import Linear_QNet, QTrainer
# from helper import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:


    def __init__(self):
        self.n_games = 0 # number of games played initially
        self.epsilon = 0 # randomness , it helps in exploration
        self.gamma = 0.9 # discount rate , # future rewards are discounted as they are less important than immediate rewards
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() , # if memory is full, remove the oldest element
        # self.model = Linear_QNet(11, 256, 3)
        # self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    
    def get_state(self, game): # get the current state of the game at a given time
            head = game.snake[0]
            point_l = Point(head.x - 20, head.y)
            point_r = Point(head.x + 20, head.y)
            point_u = Point(head.x, head.y - 20)
            point_d = Point(head.x, head.y + 20)
            
            dir_l = game.direction == Direction.LEFT
            dir_r = game.direction == Direction.RIGHT
            dir_u = game.direction == Direction.UP
            dir_d = game.direction == Direction.DOWN

            state = [ # Current state of the game in the form of a list 
                # Danger straight
                (dir_r and game.is_collision(point_r)) or 
                (dir_l and game.is_collision(point_l)) or 
                (dir_u and game.is_collision(point_u)) or 
                (dir_d and game.is_collision(point_d)),

                # Danger right
                (dir_u and game.is_collision(point_r)) or 
                (dir_d and game.is_collision(point_l)) or 
                (dir_l and game.is_collision(point_u)) or 
                (dir_r and game.is_collision(point_d)),

                # Danger left
                (dir_d and game.is_collision(point_r)) or 
                (dir_u and game.is_collision(point_l)) or 
                (dir_r and game.is_collision(point_u)) or 
                (dir_l and game.is_collision(point_d)),
                
                # Move direction
                dir_l,
                dir_r,
                dir_u,
                dir_d,
                
                # Food location 
                game.food.x < game.head.x,  # food left
                game.food.x > game.head.x,  # food right
                game.food.y < game.head.y,  # food up
                game.food.y > game.head.y  # food down
                ]

            return np.array(state, dtype=int)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = [] # list of scores for each game
    plot_mean_scores = [] # list of mean scores for each game
    total_score = 0 # total score of all games
    record = 0 # record score of the best game
    agent = Agent() # initialize agent
    game = SnakeGameAI() # initialize game
    while True:
        # get old state
        state_old = agent.get_state(game) # get current state from game

        # get move
        final_move = agent.get_action(state_old) # get action from agent based on current state

        # perform move and get new state along with reward and done status
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory using the old state, action, reward, new state and done status
        agent.train_short_memory(state_old, final_move, reward, state_new, done) 

        # remember the old state, action, reward, new state and done status for storing in memory
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()  # reset the game as the game is done
            agent.n_games += 1 # increment number of games played
            agent.train_long_memory() # train the agent using the memory

            if score > record: # if the score is greater than the record score, update the record
                record = score 
                agent.model.save() # save the model if the score is greater than the record score 

            print('Game', agent.n_games, 'Score', score, 'Record:', record) # print the game number, score and record score

            plot_scores.append(score) # append the score to the list of scores
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            #plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
