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
            head = game.snake[0] # the head of the snake
            # points one block away from the head in each direction (used for collision checks)
            point_l = Point(head.x - 20, head.y) # point to the left of the head to check for collision, if snake is moving left if point_l macthes the left wall point or snake's body, it will be a collision
            point_r = Point(head.x + 20, head.y) # point to the right of the head to check for collision, if snake is moving right if point_r matches the right wall point or snake's body, it will be a collision
            point_u = Point(head.x, head.y - 20)
            point_d = Point(head.x, head.y + 20)
            
            # checking the direction of the snake
            # if the snake is moving left, dir_l will be True, else False, game.direction will be given by the game object if it matches the Direction enum for left, right, up or down
            # the snake will be moving in one of the four directions, so we check if the game.direction matches any of the four directions
            dir_l = game.direction == Direction.LEFT
            dir_r = game.direction == Direction.RIGHT
            dir_u = game.direction == Direction.UP
            dir_d = game.direction == Direction.DOWN

            state = [ # Current state of the game in the form of a list 
                # Feature 1: Danger straight ahead - Will snake collide if it continues in current direction?
                (dir_r and game.is_collision(point_r)) or # If moving right, check collision to the right
                (dir_l and game.is_collision(point_l)) or  # If moving left, check collision to the left
                (dir_u and game.is_collision(point_u)) or 
                (dir_d and game.is_collision(point_d)),

                # Feature 2: Danger to the right - Will snake collide if it turns right from current direction?
                (dir_u and game.is_collision(point_r)) or # if moving up, will point right to us give a collision?
                (dir_d and game.is_collision(point_l)) or # if moving down, will point left to us give a collision?
                (dir_l and game.is_collision(point_u)) or 
                (dir_r and game.is_collision(point_d)),

                # Feature 3: Danger to the left - Will snake collide if it turns left from current direction?
                (dir_d and game.is_collision(point_r)) or # if moving down, will point right to us give a collision?
                (dir_u and game.is_collision(point_l)) or  # if moving up, will point left to us give a collision?
                (dir_r and game.is_collision(point_u)) or 
                (dir_l and game.is_collision(point_d)),
                
                # Features 4-7: Current movement direction (one-hot encoding - only one will be True)
                dir_l, # true if moving left
                dir_r,
                dir_u,
                dir_d,
                
                # Features 8-11: Food location relative to snake's head (binary indicators)
                game.food.x < game.head.x,  # true if food is left of the snake's head
                game.food.x > game.head.x,  # true if food is right of the snake's head
                game.food.y < game.head.y,  # food up
                game.food.y > game.head.y  # food down
                ]

            return np.array(state, dtype=int) # convert the state to a numpy array of integers, dtype=int ensures that the array is of integer type
    
    def remember(self, state, action, reward, next_state, done): # remember the state, action, reward, next state and done status for training later
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self): # train the agent using the long memory i.e. the memory of all the states, actions, rewards, next states and done status
        # if the memory is greater than BATCH_SIZE, then sample a random batch of BATCH_SIZE from the memory
        # else, use the entire memory
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample) # unzip the mini_sample into five lists: states, actions, rewards, next_states and dones
        self.trainer.train_step(states, actions, rewards, next_states, dones) # train the agent using the mini_sample, this will call the train_step method of the trainer which will use the model to predict the Q values and update the weights of the model
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done): # train the agent using the short memory i.e. the current state, action, reward, next state and done status
        self.trainer.train_step(state, action, reward, next_state, done) # train the agent using the current state, action, reward, next state and done status

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
