import pygame
import random
import time
import constants
from ai import AI
from gui import Drawer


class Game2048:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
        pygame.display.set_caption("2048 AI Solver (Multi-file Ver.)")
        self.ai = AI()
        self.drawer = Drawer(self.screen)
        self.board = self.init_board()
        self.running = True

    def init_board(self):
        b = self.add_tile(0)
        return self.add_tile(b)

    def add_tile(self, board):
        empty = [i for i in range(16) if not (board & (0xF << (i * 4)))]
        if not empty:
            return board
        return board | (
            (1 if random.random() < 0.9 else 2) << (random.choice(empty) * 4)
        )

    def run(self):
        last_move, last_time = "None", 0.0
        game_over = False

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if not game_over:
                start_t = time.time()
                best_move = self.ai.get_best_move(self.board)

                if best_move != -1:
                    self.board = self.ai.logic.move(self.board, best_move)
                    self.board = self.add_tile(self.board)
                    last_move = ["UP", "DOWN", "LEFT", "RIGHT"][best_move]
                    last_time = time.time() - start_t
                else:
                    print("Game Over!")
                    game_over = True
            self.drawer.draw_board(self.board, last_move, last_time)
            pygame.time.delay(50)

        pygame.quit()


if __name__ == "__main__":
    Game2048().run()
