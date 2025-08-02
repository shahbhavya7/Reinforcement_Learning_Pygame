import pygame
import random
from enum import Enum
from collections import namedtuple

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
        
        # init game state
        self.direction = Direction.RIGHT # initial direction of the snake, Direction is an enum that represents the direction of the snake
        
        self.head = Point(self.w/2, self.h/2) # initial position of the snake's head, Point is a namedtuple that represents a point in 2D space
        # here the head is placed at the center of the game window as Point for the snake's head is initialized with the center coordinates of the window
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        # initial snake body, the snake is represented as a list of Points, where each Point is a segment of the snake's body
        # the snake starts with 3 segments, the head and two segments behind it, first segment is the head, second segment is one block to the left 
        # of the head, and third segment is two blocks to the left of the head, y coordinate remains the same for all segments
        
        self.score = 0 # initial score of the game, score is incremented when the snake eats food
        self.food = None
        self._place_food() # places the first food item on the game board, this method randomly places food on the game board
        
    def _place_food(self): # this method places food on the game board at a random position
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE # random x coordinate for food, it ensures that the food is placed 
        # within the game window and aligned with the grid
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y) # creates a Point for the food position based on the random x and y coordinates
        if self.food in self.snake: # if food is placed on the snake, place it again
            self._place_food()
        
    def play_step(self): # this is core method that runs one step of the game, it handles user input, moves the snake, checks for collisions, and 
        # updates the game state
        # 1. collect user input
        for event in pygame.event.get(): # get all events from the event queue, pygame.event.get() returns a list of events that have occurred since the last call
            # event queue is a list of events that have occurred in the game, such as key presses, mouse movements, etc.
            if event.type == pygame.QUIT: # if the user closes the game window this event is triggered
                pygame.quit() # quits the game
                quit() # exits the game
            if event.type == pygame.KEYDOWN: # if user presses a key this event is triggered, KEYDOWN means a key was pressed down
                if event.key == pygame.K_LEFT: # if the left arrow key is pressed,pygame.K_LEFT is a constant that represents the left arrow key
                    self.direction = Direction.LEFT # change the direction of the snake to left
                elif event.key == pygame.K_RIGHT: # if the right arrow key is pressed 
                    self.direction = Direction.RIGHT # change the direction of the snake to right
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        # 2. move
        self._move(self.direction) # update the position of the snake's head based on the current direction, this method updates the head position 
        # based on the direction of the snake
        self.snake.insert(0, self.head) # .insert takes an index and an element, it inserts the head at the beginning of the snake list
        # this adds the new head position to the front of the snake list, so the snake grows in length, snake list is a list of Points representing the snake's body
        
        # 3. check if game over
        game_over = False # initialize game_over to False, it will be set to True if the snake collides with itself or the boundaries of the game window
        if self._is_collision(): # check for collisions, this method checks if the snake has collided with itself or the boundaries of the game window
            game_over = True
            return game_over, self.score # if there is a collision, return game_over and score
            
        # 4. place new food or just move
        if self.head == self.food: # if the snake's head is at the same position as the food, it means the snake has eaten the food
            self.score += 1 # increment the score by 1
            self._place_food() # place new food at a random position, this method places food at a random position on the game board
        else:
            self.snake.pop() # remove the last segment of the snake, this keeps the snake's length constant if it hasn't eaten food, .pop() removes the last element from the list
        
        # 5. update ui and clock
        self._update_ui() # update the game display, this method updates the game display by drawing the snake and food on the screen using pygame's drawing functions
        self.clock.tick(SPEED) # control the frame rate of the game, this method limits the game to run at a certain speed, SPEED is the number of frames per second
        # 6. return game over and score
        return game_over, self.score # return the game_over status and the current score after processing the step
    
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
        # if the head of the snake is outside the boundaries of the game window, it means the snake has collided with the boundary
            return True
        # hits itself
        if self.head in self.snake[1:]: # if the head of the snake is in the snake list excluding the first element (the head itself), it means the snake has collided with itself
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
        
    def _move(self, direction): # this method updates the position of the snake's head based on the current direction
        x = self.head.x # get the current x coordinate of the snake's head 
        y = self.head.y
        if direction == Direction.RIGHT: # if the direction is right, move the head to the right by BLOCK_SIZE
            x += BLOCK_SIZE
        elif direction == Direction.LEFT: # if the direction is left, move the head to the left by BLOCK_SIZE
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN: # if the direction is down, move the head down by BLOCK_SIZE
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y) # update the head position with the new coordinates, this creates a new Point for the head with the updated x and y coordinates
            

if __name__ == '__main__':
    game = SnakeGame() # create an instance of the SnakeGame class, this initializes the game and sets up the game window, snake, food, and other 
    # game state variables
    
    # game loop
    while True:
        game_over, score = game.play_step() # play a step of the game, this method handles user input, moves the snake, checks for collisions, and updates the game state
        
        if game_over == True: # if the game is over, break the loop
            break
        
    print('Final Score', score) # print the final score when the game is over
        
        
    pygame.quit() # quit the game when the game loop ends, this closes the game window and cleans up resources