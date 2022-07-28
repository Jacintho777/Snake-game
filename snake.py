############################### A LITTLE SNAKE GAME ##################################################
######################################################################################################

import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()

font = pygame.font.Font('cmu.ttf',25)
game_over_font = pygame.font.Font('cmu.ttf',32)

class Direction(Enum):
	RIGHT = 1
	LEFT = 2
	UP = 3
	DOWN = 4

Point = namedtuple('Point','x, y')

BLOCK_SIZE = 20
SPEED = 1 #make this dependant of the size of the snake

#colors
BLACK = (0,0,0)
BLACK_TRANS = (0,0,0,128)
WHITE = (255,255,255)
RED = (200,0,0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)
# BLUE3 = (25,30,161)
YELLOW = (255,255,0)
GRAY = (192,192,192)

#music
crunch = pygame.mixer.Sound('crunch.ogg')
game_over_sound = pygame.mixer.Sound('game-over-arcade-6435.ogg')

class SnakeGame:

	def __init__(self,w = 640,h = 480):
		
		self.w = w
		self.h = h
		#init display
		self.margin = 60 #height of the bottom band
		self.display = pygame.display.set_mode((self.w, self.h+self.margin))
		pygame.display.set_caption('Snake')
		self.clock = pygame.time.Clock()
		self.chrono = 0

		#init game state
		self.lets_move = False
		self.direction = Direction.RIGHT

		self.head = Point(self.w/2,self.h/2)
		self.snake = [self.head, Point(self.head.x-BLOCK_SIZE,self.head.y),Point(self.head.x-2*BLOCK_SIZE,self.head.y)]

		self.score = 0
		self.best_score = 0

		#grab the best_score from the database
		try:
			database = open('best_score.txt','r')
			self.best_score = int(database.readlines()[0])
			database.close()
		except:
			database = open('best_score.txt','w')
			database.close()

		self.eats = 0
		self.food = None
		self.yummy = None
		self.yummy_life = 4000

		self._place_food()

	def _place_food(self):
		x = random.randint(0,(self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
		y =  random.randint(0,(self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE	
		self.food = Point(x,y)

		if self.food in self.snake: #Don't place it in the snake
			self._place_food()

	def _place_yummy(self):
		x = random.randint(0,(self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
		y =  random.randint(0,(self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE	
		self.yummy = Point(x,y)

		#Yummy life stuffs
		self.chrono = pygame.time.get_ticks()
		print(self.chrono)
		self.yummy_radius = BLOCK_SIZE*1.5

		if self.yummy in self.snake: #Don't place it in the snake
			self._place_yummy()

	def play_step(self):
		#1.collect user input
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				self.lets_move = True
				if event.key == pygame.K_LEFT:
					self.direction = Direction.LEFT
				elif event.key == pygame.K_RIGHT:
					self.direction = Direction.RIGHT
				elif event.key == pygame.K_UP:
					self.direction = Direction.UP
				elif event.key == pygame.K_DOWN:
					self.direction = Direction.DOWN

		#2.move
		if self.lets_move:
			self.move(self.direction)

		#3.check if gameover
		game_over = False
		if self._is_collision():
			pygame.mixer.Sound.play(game_over_sound)
			game_over = True
			pygame.time.delay(1200)
	
			#Recording the best score
			if self.score > self.best_score:
				database = open("best_score.txt",'w')
				database.write(str(self.score))
				database.close()

			return game_over,self.score

		#4.Place new food or just move
		if self.eats%5 == 0 and self.head == self.yummy and self.yummy_radius!=0: #Eat yummy gives more points
			self.score += 2 
			self.eats += 1
			pygame.mixer.Sound.play(crunch)

		if self.head == self.food:
			self.score += 1
			self.eats += 1
			pygame.mixer.Sound.play(crunch)
			self._place_food()
			if self.eats%5 == 0 and self.eats != 0: 
				self._place_yummy()

		#if he eats it's fine but if not we substract the tail after adding the head (lengthening effect) 
		else:
			if self.lets_move:
				self.snake.pop()

		#5. update ui and clock
		self.update_ui()
		self.clock.tick(SPEED*len(self.snake))

		#6. return game over
		game_over = False
		return game_over

	def _is_collision(self):
		#hits boundary
		if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
			return True
		#hits itself
		if self.head in self.snake[1:]:
			return True

		return False

	def update_ui(self):

		self.display.fill(BLACK)

		#drawing the snake
		for pt in self.snake:
			pygame.draw.rect(self.display,BLUE1, pygame.Rect(pt.x,pt.y,BLOCK_SIZE,BLOCK_SIZE))
			pygame.draw.rect(self.display,BLUE2, pygame.Rect(pt.x+4,pt.y+4,12,12)) #why? draws the small squares inside the bigger ones

		#drawing the food
		pygame.draw.circle(self.display, RED, (self.food.x+BLOCK_SIZE/2,self.food.y+BLOCK_SIZE/2),radius = BLOCK_SIZE/2)
		if self.eats%5 == 0 and self.eats != 0 and self.yummy_radius!=0:
			if 0 < pygame.time.get_ticks()-self.chrono < self.yummy_life:
				print(pygame.time.get_ticks()-self.chrono )
				self.yummy_radius = BLOCK_SIZE*1.5*(1-(pygame.time.get_ticks()-self.chrono)/self.yummy_life)
			else:
				self.yummy_radius = 0
			pygame.draw.circle(self.display, YELLOW, (self.yummy.x+BLOCK_SIZE/2,self.yummy.y+BLOCK_SIZE/2),radius = self.yummy_radius)

		#printing the labels
		pygame.draw.rect(self.display,WHITE,pygame.Rect(0,self.h,self.w,self.margin)) #Displaying the band

		text_score = font.render("Score : "+str(self.score),True,BLACK)
		text_best_score = font.render("Best score : "+str(self.best_score),True,BLACK)

		self.display.blit(text_score,[self.w/5.5-25,self.h+(self.margin/4)])
		self.display.blit(text_best_score,[275+self.w/5.5,self.h+(self.margin/4)])

		pygame.display.flip()
	
	def show_game_over(self):

		restart_button_posx,restart_button_posy = 270,250
		restart_button_width,restart_button_height = 100,40
		restart = False

		for event in pygame.event.get(): # Wanna quit the game after game over
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse = pygame.mouse.get_pos()
				if restart_button_posx<=mouse[0]<=restart_button_posx+restart_button_width and restart_button_posy<=mouse[1]<=restart_button_posy+restart_button_height:
					restart = True

		transparent = pygame.Surface((self.w,self.h), pygame.SRCALPHA)   # per-pixel alpha
		transparent.fill((0,0,0,140))                         # notice the alpha value in the color

		pygame.draw.rect(self.display,GRAY, pygame.Rect(restart_button_posx,restart_button_posy,restart_button_width,restart_button_height)) #Restart button rectangle

		text_game_over = game_over_font.render("GAME OVER !",True,WHITE)
		text_restart = font.render("Restart",True,WHITE)

		self.display.blit(transparent, (0,0))
		self.display.blit(text_game_over,[self.w/2-110,self.h/2-80])
		self.display.blit(text_restart,[restart_button_posx+4,restart_button_posy+2])

		pygame.display.flip()

		return restart

	def move(self,direction):
		
		x = self.head.x
		y = self.head.y

		if direction == Direction.RIGHT:
			x += BLOCK_SIZE
		elif direction == Direction.LEFT:
			x -= BLOCK_SIZE
		elif direction == Direction.DOWN:
			y += BLOCK_SIZE
		elif direction == Direction.UP:
			y -= BLOCK_SIZE

		if Point(x,y) not in self.snake[0:2]: # Not to make game over backward
			self.head = Point(x,y)
			self.snake.insert(0,self.head)

		else:
			#making sure snake doesn't collide 
			#when we go in the straight opposite direction
			if direction == Direction.RIGHT:
				self.move(Direction.LEFT)
			elif direction == Direction.LEFT:
				self.move(Direction.RIGHT)
			elif direction == Direction.UP:
				self.move(Direction.DOWN)
			elif direction == Direction.DOWN:
				self.move(Direction.UP)

def main():
	game = SnakeGame()

	game_over = game.play_step()

	#game loop
	while True:

		if game_over:
			restart = game.show_game_over()
			if restart == True:
				main()
		else:
			game_over = game.play_step()

if __name__ == "__main__":

	main()

# Jacintho MPETEYE #