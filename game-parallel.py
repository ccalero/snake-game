import random
import pygame
import sys
import threading
import psutil

from pygame.locals import *

#Tamanio de la ventana
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480

#Tamanio de la celda
CELL_SIZE = 20

#Nro de celdas
CELL_WIDTH = int(DISPLAY_WIDTH / CELL_SIZE)
CELL_HEIGHT = int(DISPLAY_HEIGHT / CELL_SIZE)

NUM_SNAKES = 5
SNAKES = []
WAIT_SNAKE = 200
SNAKES_STOP = False
TAM_MAX = 5

ID_PLAYER = 0

WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
RED         = (255,   0,   0)
GREEN       = (  0, 255,   0)
BLUE        = (  0,   0, 255)

HORIZONTAL = 0
VERTICAL = 1

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

class Snake(threading.Thread):
    #inicia el hilo
    def __init__(self, id = 0, autoControl = True):
        threading.Thread.__init__(self)

        self.id = id
        self.autoControl = autoControl
        self.direction = RIGHT
        self.color = [random.randrange(0, 200),random.randrange(0, 200),random.randrange(0, 200)]
        self.snakeCoords = []
        self.HEAD = 0

        if self.id == ID_PLAYER:
            self.autoControl = False
            self.color = WHITE

        #1: vertical, 0: horizontal
        position = random.randint(0,1)

        #bucle para encontrar unas celdas vacia
        while True:
            startx = random.randint(5, CELL_WIDTH - 6)
            starty = random.randint(5, CELL_HEIGHT - 6)

            cells_fill = False;
            #Se bloquea la celda donde empieza la serpiente
            for i in range(TAM_MAX):
                if position == HORIZONTAL:
                    if GRID[startx - i][starty] is not None:
                        cells_fill = True
                else:
                    if GRID[startx][starty - i] is not None:
                        cells_fill = True

            if cells_fill is False:
                break

        for i in range(TAM_MAX):
            if position == HORIZONTAL:
                self.snakeCoords.append({'x': startx - i, 'y': starty})
            else:
                self.snakeCoords.append({'x': startx, 'y': starty - i})

    #Ejecuta el hilo
    def run(self):
        while True:
            #Flag para parar el juego y borrar todos las serpientes
            if SNAKES_STOP:
                self.removeSnake()
                return

            head_x = self.snakeCoords[self.HEAD]['x']
            head_y = self.snakeCoords[self.HEAD]['y']

            #Comprobamos si la serpiente choca
            if head_x == 0 or head_x == CELL_WIDTH-1 or head_y == 0 or head_y == CELL_HEIGHT-1:
                self.removeSnake()
                return # game over

            #Comprobamos si la serpiente choca contra si mismo
            for snakeBody in self.snakeCoords[1:]:
                if snakeBody['x'] == head_x and snakeBody['y'] == head_y:
                    self.removeSnake()
                    return # game over

            #Mueve el gusando aniadiendo un cuadrado en la direccion
            if self.direction == UP:
                newHead = {'x': head_x, 'y': head_y - 1}
                if GRID[newHead['x']][newHead['y']] is not None:
                    self.removeSnake()
                    return
            elif self.direction == DOWN:
                newHead = {'x': head_x, 'y': head_y + 1}
                if GRID[newHead['x']][newHead['y']] is not None:
                    self.removeSnake()
                    return
            elif self.direction == LEFT:
                newHead = {'x': head_x - 1, 'y': head_y}
                if GRID[newHead['x']][newHead['y']] is not None:
                    self.removeSnake()
                    return
            elif self.direction == RIGHT:
                newHead = {'x': head_x + 1, 'y': head_y}
                if GRID[newHead['x']][newHead['y']] is not None:
                    self.removeSnake()
                    return
            else:
                newHead = {'x': head_x, 'y': head_y}

            #insertamos la nueva seccion en el array del serpiente
            self.snakeCoords.insert(0, newHead)

            #borramos la ultima seccion
            GRID[self.snakeCoords[-1]['x']][self.snakeCoords[-1]['y']] = None
            del self.snakeCoords[-1] # borramos la cola del serpiente

            #pintamos
            self.drawSnake()
            pygame.time.wait(WAIT_SNAKE)

            if self.autoControl:
                self.direction = self.getDirection()

    #Borra la serpiente del array de todos y lo borra del grid
    def removeSnake(self):
        SNAKES.remove(self)
        for coord in self.snakeCoords:
            GRID[coord['x']][coord['y']] = None

    #pinta en el grid
    def drawSnake(self):
        for coord in self.snakeCoords:
            GRID[coord['x']][coord['y']] = self.color

    #Obtiene una direccion aleatoria
    def getDirection(self):
        change_direction = random.randint(0,1)

        x = self.snakeCoords[self.HEAD]['x']
        y = self.snakeCoords[self.HEAD]['y']

        if change_direction:
            newDirection = []
            if y - 1 not in (-1, CELL_HEIGHT) and GRID[x][y - 1] is None:
                newDirection.append(UP)
            if y + 1 not in (-1, CELL_HEIGHT) and GRID[x][y + 1] is None:
                newDirection.append(DOWN)
            if x - 1 not in (-1, CELL_WIDTH) and GRID[x - 1][y] is None:
                newDirection.append(LEFT)
            if x + 1 not in (-1, CELL_WIDTH) and GRID[x + 1][y] is None:
                newDirection.append(RIGHT)

            if newDirection == []:
                return None # None is returned when there are no possible ways for the snake to move.
            return random.choice(newDirection)
        else:
            if self.direction == UP and y - 1 not in (-1, CELL_HEIGHT) and GRID[x][y - 1] is None:
                return self.direction
            elif self.direction == DOWN and y + 1 not in (-1, CELL_HEIGHT) and GRID[x][y + 1] is None:
                return self.direction
            elif self.direction == LEFT  and x - 1 not in (-1, CELL_WIDTH) and GRID[x - 1][y] is None:
                return self.direction
            elif self.direction == RIGHT and x + 1 not in (-1, CELL_WIDTH) and GRID[x + 1][y] is None:
                return self.direction
            else:
                self.getDirection()

#Bucle del Juego
def gameLoop():
    #Creamos las serpientes e iniciamos los hilos
    for i in range(NUM_SNAKES):
        SNAKES.append(Snake(id = i))
        SNAKES[-1].start()

    id_aux = NUM_SNAKES
    while True:
        drawGrid()

        events = pygame.event.get(pygame.KEYDOWN)
        for event in events:
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                terminate()

            if event.key == K_LEFT and SNAKES[ID_PLAYER].direction != RIGHT:
                SNAKES[ID_PLAYER].direction = LEFT
            elif event.key == K_RIGHT and SNAKES[ID_PLAYER].direction != LEFT:
                SNAKES[ID_PLAYER].direction = RIGHT
            elif event.key == K_UP and SNAKES[ID_PLAYER].direction != DOWN:
                SNAKES[ID_PLAYER].direction = UP
            elif event.key == K_DOWN and SNAKES[ID_PLAYER].direction != UP:
                SNAKES[ID_PLAYER].direction = DOWN

            elif event.key == K_F1:
                SNAKES.append(Snake(id=id_aux))
                SNAKES[-1].start()
                id_aux+=1
            elif event.key == K_F2:
                if SNAKES[ID_PLAYER].autoControl is False:
                    SNAKES[ID_PLAYER].autoControl = True
                else:
                    SNAKES[ID_PLAYER].autoControl = False

        pygame.display.update()
        pygame.time.Clock().tick(WAIT_SNAKE)

        if len(SNAKES) == 0:
            showGameOverScreen()
            gameLoop()

def drawGrid():
    WINDOW.blit(BCK_IMG, (0, 0))

    for x in range(0, CELL_WIDTH):
        for y in range(0, CELL_HEIGHT):
            if GRID[x][y] is None:
                pygame.draw.rect(WINDOW, BLACK, (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1))
            else:
                color = GRID[x][y]
                darkerColor = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
                pygame.draw.rect(WINDOW, darkerColor, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(WINDOW, color, (x * CELL_SIZE + 4, y * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8))

def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    overSurf = gameOverFont.render('FIN', True, WHITE)
    overRect = overSurf.get_rect()
    overRect.midtop = (DISPLAY_WIDTH / 2, 30 + 10 + 25)

    WINDOW.blit(overSurf, overRect)
    pygame.display.update()
    pygame.time.wait(500)

def terminate():
    pygame.quit()
    sys.exit()

pygame.init()

#Mostramos ventana
WINDOW = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
BCK_IMG = pygame.image.load('land.png')

WINDOW.blit(BCK_IMG, (0, 0))

GRID = []
for x in range(CELL_WIDTH):
    GRID.append([None] * CELL_HEIGHT)

while True:
    pygame.time.wait(500)
    gameLoop()
