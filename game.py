import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25) # it means you need to have 'arial.ttf' in the same directory as this script
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum): # This enum is used to represent the direction of the snake
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y') # namedtuple creates a simple class to represent a point in 2D space, here used for snake segments and food position
# Point means a point in 2D space with x and y coordinates and its assigned to Point class

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20 # size of each block in the snake, this is the size of each segment of the snake and also the size of the food
# BLOCK_SIZE is used to determine the size of the snake segments and the food, it is also used to calculate the position of the snake and food in 
# the game window
SPEED = 9

class SnakeGame: # This class encapsulates the game logic and state
    
    def __init__(self, w=640, h=480): # constructor initializes the game, # w and h are the width and height of the game window
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h)) # creates a window of size w x h, pygame.display.set_mode() initializes the game window
        pygame.display.set_caption('Snake') # sets the title of the game window
        self.clock = pygame.time.Clock() # creates a clock object to control the frame rate of the game i.e. how fast the game updates
        self.reset() # reset the game state to the initial state, this method initializes the game state variables such as direction, snake position, food position, and score
        
        # # init game state
        # self.direction = Direction.RIGHT # initial direction of the snake, Direction is an enum that represents the direction of the snake
        
        # self.head = Point(self.w/2, self.h/2) # initial position of the snake's head, Point is a namedtuple that represents a point in 2D space
        # # here the head is placed at the center of the game window as Point for the snake's head is initialized with the center coordinates of the window
        # self.snake = [self.head, 
        #               Point(self.head.x-BLOCK_SIZE, self.head.y),
        #               Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        # # initial snake body, the snake is represented as a list of Points, where each Point is a segment of the snake's body
        # # the snake starts with 3 segments, the head and two segments behind it, first segment is the head, second segment is one block to the left 
        # # of the head, and third segment is two blocks to the left of the head, y coordinate remains the same for all segments
        
        # self.score = 0 # initial score of the game, score is incremented when the snake eats food
        # self.food = None
        # self._place_food() # places the first food item on the game board, this method randomly places food on the game board
        
        
        
    def reset(self): # this method resets the game state to the initial state
        self.direction = Direction.RIGHT 
        
        self.head = Point(self.w/2, self.h/2) 
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0 
        self.food = None
        self._place_food() 
        self.frame_iteration = 0 # this variable is used to keep track of the number of frames that have been played, it can be used for debugging or other purposes
        
        
    def _place_food(self): # this method places food on the game board at a random position
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE # random x coordinate for food, it ensures that the food is placed 
        # within the game window and aligned with the grid
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y) # creates a Point for the food position based on the random x and y coordinates
        if self.food in self.snake: # if food is placed on the snake, place it again
            self._place_food()
        
    def play_step(self,action): # this is core method that runs one step of the game, it handles user input, moves the snake, checks for collisions, and 
        # updates the game state
        self.frame_iteration += 1 # increment the frame iteration, this keeps track of how many frames have been played
        # 1. collect user input
        for event in pygame.event.get(): # get all events from the event queue, pygame.event.get() returns a list of events that have occurred since the last call
            # event queue is a list of events that have occurred in the game, such as key presses, mouse movements, etc.
            if event.type == pygame.QUIT: # if the user closes the game window this event is triggered
                pygame.quit() # quits the game
                quit() # exits the game

        
        # 2. move
        self._move(action) # update the position of the snake's head based on the current direction, this method updates the head position 
        # based on the direction of the snake
        self.snake.insert(0, self.head) # .insert takes an index and an element, it inserts the head at the beginning of the snake list
        # this adds the new head position to the front of the snake list, so the snake grows in length, snake list is a list of Points representing the snake's body
        
        # 3. check if game over
        reward = 0 # initialize reward to 0, it can be used for reinforcement learning purposes, but in this case, it is not used
        game_over = False # initialize game_over to False, it will be set to True if the snake collides with itself or the boundaries of the game window
        if self._is_collision() or self.frame_iteration > 100*len(self.snake): # check for collisions, this method checks if the snake has collided with 
            #itself or the boundaries of the game window or if the snake has been alive for too long (more than 100 times its length)
            game_over = True
            reward = -10 # if there is a collision, set reward to -10, this can be used for reinforcement learning purposes
            return reward, game_over, self.score # if there is a collision, return game_over and score
            
        # 4. place new food or just move
        if self.head == self.food: # if the snake's head is at the same position as the food, it means the snake has eaten the food
            self.score += 1 # increment the score by 1
            reward = 10 # set reward to 10, this can be used for reinforcement learning purposes
            self._place_food() # place new food at a random position, this method places food at a random position on the game board
        else:
            self.snake.pop() # remove the last segment of the snake, this keeps the snake's length constant if it hasn't eaten food, .pop() removes the last element from the list
        
        # 5. update ui and clock
        self._update_ui() # update the game display, this method updates the game display by drawing the snake and food on the screen using pygame's drawing functions
        self.clock.tick(SPEED) # control the frame rate of the game, this method limits the game to run at a certain speed, SPEED is the number of frames per second
        # 6. return game over and score
        return reward, game_over, self.score # return the game_over status and the current score after processing the step
    
    def _is_collision(self,pt=None):
        if pt is None: # if pt is not provided, use the snake's head position
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
        # if the head of the snake is outside the boundaries of the game window, it means the snake has collided with the boundary
            return True
        # hits itself
        if pt in self.snake[1:]: # if the head of the snake is in the snake list excluding the first element (the head itself), it means the snake has collided with itself
            return True
        
        return False
        
    def _update_ui(self): # this method updates the game display by drawing the snake and food on the screen
        self.display.fill(BLACK) # fill the game window with black color, this clears the previous frame
        
        for pt in self.snake: # iterate through each segment of the snake and draw it on the screen
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) # draw the snake segment with a blue color
            # pygame.draw.rect() draws a rectangle on the screen, it takes the surface to draw on, the color, and a rectangle defined by a Point (x, y) and size (width, height)
            # here pt.x and pt.y are the coordinates of the segment, BLOCK_SIZE is the size of the segment, so each segment is drawn as a square of size BLOCK_SIZE
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12)) # draw a smaller rectangle inside the segment to create a border effect
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE)) # draw the food on the screen, 
        # food is drawn as a red square at the position of the food Point
        
        text = font.render("Score: " + str(self.score), True, WHITE) # render the score text, font.render() creates a new surface with the text, it takes the text to render, antialiasing (True), and the color of the text
        self.display.blit(text, [0, 0]) # blit() draws the text surface on the game display at the specified position, here it is drawn at the top left corner of the screen
        pygame.display.flip() # update the display to show the new frame, pygame.display.flip() updates the entire display surface to the screen
        
    def _move(self, action): # this method updates the position of the snake's head based on the current direction
        
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP] # list of directions in clockwise order
        idx = clock_wise.index(self.direction) # get the index of the current direction in the clockwise list
        
        if np.array_equal(action, [1, 0, 0]): # if the action is to move right
            new_dir = clock_wise[idx] # keep the current direction
        elif np.array_equal(action, [0, 1, 0]): # if the action is to move down
            new_dir = clock_wise[(idx + 1) % 4] # change
            # to the next direction in the clockwise list, % 4 ensures that the index wraps around if it goes beyond the last index
        else:
            new_dir = clock_wise[(idx - 1) % 4] # change to the previous direction in the clockwise list, % 4 ensures that the index wraps around if it goes below 0
            
        self.direction = new_dir
        
        x = self.head.x # get the current x coordinate of the snake's head 
        y = self.head.y
        if self.direction == Direction.RIGHT: # if the direction is right, move the head to the right by BLOCK_SIZE
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT: # if the direction is left, move the head to the left by BLOCK_SIZE
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN: # if the direction is down, move the head down by BLOCK_SIZE
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y) # update the head position with the new coordinates, this creates a new Point for the head with the updated x and y coordinates
            

