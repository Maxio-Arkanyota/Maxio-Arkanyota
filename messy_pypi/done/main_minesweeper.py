import os
from enum import Enum, auto
from random import randint

import pygame


class Main:
    @staticmethod
    def start():
        pygame.font.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (400, 100)
        surface = pygame.display.set_mode((1200, 900))
        pygame.display.set_caption('Minesweeper')
        state = States.running
        player = Player()
        grid = Grid(player)
        running = True
        clock = pygame.time.Clock()
        while running:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and state == States.running:
                    if pygame.mouse.get_pressed()[0]:
                        pos = pygame.mouse.get_pos()
                        grid.click(pos[0], pos[1])
                    elif pygame.mouse.get_pressed()[2]:
                        pos = pygame.mouse.get_pos()
                        grid.mark_mine(pos[0] // 30, pos[1] // 30)
                    if grid.check_if_win():
                        state = States.win
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and (state == States.game_over or state == States.win):
                        grid.reload()
                        state = States.running
                    if event.key == pygame.K_b:
                        grid.show_mines()
            surface.fill((0, 0, 0))
            if player.get_health() == 0:
                state = States.game_over
            if state == States.game_over:
                Stats.draw(surface, 'Game over!', (970, 350))
                Stats.draw(surface, 'Press Space to restart', (920, 400))
            elif state == States.win:
                Stats.draw(surface, 'You win!', (1000, 350))
                Stats.draw(surface, 'Press Space to restart', (920, 400))
            grid.draw(surface)
            Stats.draw(surface, 'Lives remaining', (950, 100))
            Stats.draw(surface, str(player.get_health()), (1020, 200))
            pygame.display.flip()


class States(Enum):
    running = auto()
    game_over = auto()
    win = auto()


class Player:
    def __init__(self):
        self.health = 5

    def sub_health(self):
        self.health -= 1

    def get_health(self):
        return self.health


class Stats:
    @staticmethod
    def draw(surface, label, pos):
        textsurface = pygame.font.SysFont('Comic Sans MS', 24).render(label, False, (255, 255, 255))
        surface.blit(textsurface, (pos[0], pos[1]))


class Cell:
    def __init__(self, pos, random_mine):
        self.visible = False
        self.mine = random_mine
        self.show_mine = False
        self.size = 30
        self.color = (200, 200, 200)
        self.pos = pos
        self.label = False
        self.mine_counter = 0
        self.font_color = (0, 0, 0)
        self.marked = False
        self.explosion = False
        self.img_flag = pygame.image.load('../resources/minesweeper/cell-flagged.png')
        self.img_flag = pygame.transform.scale(self.img_flag, (self.size, self.size))

        self.img_explode = pygame.image.load('../resources/minesweeper/mine-exploded.png')
        self.img_explode = pygame.transform.scale(self.img_explode, (self.size, self.size))

        self.img_mine = pygame.image.load('../resources/minesweeper/mine.png')
        self.img_mine = pygame.transform.scale(self.img_mine, (self.size, self.size))

        self.img_cell = []
        for i in range(9):
            _img = pygame.image.load(f'../resources/minesweeper/cell-{i}.png')
            _img = pygame.transform.scale(_img, (self.size, self.size))
            self.img_cell.append(_img)

    def draw(self, surface):
        if self.visible and not self.label and not (self.show_mine and self.mine):
            surface.blit(self.img_cell[0], (self.pos[0], self.pos[1]))
        elif self.label:
            self.show_label(surface, self.mine_counter, self.pos)
        elif self.marked:
            surface.blit(self.img_flag, (self.pos[0], self.pos[1]))
        elif self.show_mine and self.mine:
            surface.blit(self.img_mine, (self.pos[0], self.pos[1]))
        elif self.explosion:
            surface.blit(self.img_explode, (self.pos[0], self.pos[1]))
        else:
            pygame.draw.rect(surface, (50, 50, 50), (self.pos[0], self.pos[1], self.size, self.size))

    def show_label(self, surface, label, pos):
        # textsurface = pygame.font.SysFont('Comic Sans MS', 18).render(label, False, self.font_color)
        # surface.blit(textsurface, (pos[0] + 10, pos[1] + 4))
        surface.blit(self.img_cell[int(label)], (pos[0], pos[1]))


class Grid:
    def __init__(self, player):
        self.player = player
        self.cells = []
        self.search_dirs = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]

        for y in range(30):
            self.cells.append([])
            for x in range(30):
                self.cells[y].append(Cell((x * 30, y * 30), self.random_mines()))

        self.lines = []

        for y in range(1, 31, 1):
            temp = []
            temp.append((0, y * 30))
            temp.append((900, y * 30))
            self.lines.append(temp)

        for x in range(1, 31, 1):
            temp = []
            temp.append((x * 30, 0))
            temp.append((x * 30, 900))
            self.lines.append(temp)

    def random_mines(self):
        r = randint(0, 10)
        if r > 9:
            return True
        else:
            return False

    def draw(self, surface):
        for row in self.cells:
            for cell in row:
                cell.draw(surface)
        for line in self.lines:
            pygame.draw.line(surface, (0, 125, 0), line[0], line[1])

    def is_within_bounds(self, x, y):
        return x >= 0 and x < 30 and y >= 0 and y < 30

    def search(self, x, y):
        if not self.is_within_bounds(x, y):
            return

        cell = self.cells[y][x]

        if cell.visible:
            return

        if cell.mine:
            cell.explosion = True
            self.player.sub_health()
            return

        cell.visible = True

        num_mines = self.num_of_mines(x, y)

        if num_mines > 0:
            cell.label = True
            cell.mine_counter = str(num_mines)
            return

        for xx, yy in self.search_dirs:
            self.search(x + xx, y + yy)

    def num_of_mines(self, x, y):
        counter = 0
        for xx, yy in self.search_dirs:
            if self.is_within_bounds(x + xx, y + yy) and self.cells[y + yy][x + xx].mine:
                counter += 1
        return counter

    def click(self, x, y):
        grid_x, grid_y = x // 30, y // 30
        self.search(grid_x, grid_y)

    def reload(self):
        self.player.health = 5
        for row in self.cells:
            for cell in row:
                cell.visible = False
                cell.label = False
                cell.marked = False
                cell.show_mine = False
                cell.explosion = False
                cell.mine = self.random_mines()

    def check_if_win(self):
        if self.player.health < 1:
            return False
        for row in self.cells:
            for cell in row:
                if not cell.visible and not cell.mine:
                    return False
        return True

    def show_mines(self):
        for row in self.cells:
            for cell in row:
                if not cell.show_mine:
                    cell.show_mine = True
                else:
                    cell.show_mine = False

    def mark_mine(self, x, y):
        self.cells[y][x].marked = True


if __name__ == "__main__":
    Main.start()
