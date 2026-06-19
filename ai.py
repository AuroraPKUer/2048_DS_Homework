import random
import constants
from logic import GameLogic


class AI:
    def __init__(self):
        self.logic = GameLogic()

    def evaluate(self, board):
        score = constants.LOST_PENALTY
        t_board = self.logic.transpose(board)

        rows = []
        max_val = 0

        for i in range(4):
            row_val = (board >> (i * 16)) & 0xFFFF
            rows.append(row_val)

            for j in range(4):
                tile = (row_val >> (j * 4)) & 0xF
                if tile > max_val:
                    max_val = tile

            score += self.logic.get_row_info(row_val)[1]
            score += self.logic.get_row_info((t_board >> (i * 16)) & 0xFFFF)[1]

        corners = [
            (rows[0] & 0xF),
            (rows[0] >> 12) & 0xF,
            (rows[3] & 0xF),
            (rows[3] >> 12) & 0xF,
        ]

        if max_val not in corners:
            score -= getattr(constants, "NOT_IN_CORNER_PENALTY", 20000.0) * max_val

        penalty_empty = getattr(constants, "EMPTY_ROW_PENALTY", 50000.0)
        if rows[0] != 0 and rows[1] != 0 and rows[2] == 0:
            score -= penalty_empty
        if rows[0] != 0 and rows[1] != 0 and rows[2] != 0 and rows[3] == 0:
            score -= penalty_empty

        if rows[0] != 0 and rows[1] != 0 and rows[2] != 0:
            can_merge = False
            for i in range(3):
                line = [(rows[i] >> (4 * j)) & 0xF for j in range(4)]
                for j in range(3):
                    if line[j] != 0 and line[j] == line[j + 1]:
                        can_merge = True
                        break
                if can_merge:
                    break

            if not can_merge:
                for i in range(2):
                    line_top = [(rows[i] >> (4 * j)) & 0xF for j in range(4)]
                    line_bot = [(rows[i + 1] >> (4 * j)) & 0xF for j in range(4)]
                    for j in range(4):
                        if line_top[j] != 0 and line_top[j] == line_bot[j]:
                            can_merge = True
                            break
                    if can_merge:
                        break

            if not can_merge:
                score -= getattr(constants, "NO_MERGE_PENALTY", 30000.0)

        return score

    def expectiminimax(self, board, depth, is_ai):
        if depth == 0:
            return self.evaluate(board)

        if is_ai:
            best_val = -float("inf")
            for d in range(4):
                nb = self.logic.move(board, d)
                if nb != board:
                    best_val = max(best_val, self.expectiminimax(nb, depth - 1, False))
            return best_val
        else:
            empty = [i for i in range(16) if not (board & (0xF << (i * 4)))]
            if not empty:
                return self.evaluate(board)
            res = 0
            slots = random.sample(empty, min(len(empty), 4))
            for slot in slots:
                res += (
                    self.expectiminimax(board | (1 << (slot * 4)), depth - 1, True)
                    * 0.9
                )
                res += (
                    self.expectiminimax(board | (2 << (slot * 4)), depth - 1, True)
                    * 0.1
                )
            return res / len(slots)

    def get_dynamic_depth(self, board):
        # empty_count = 0
        # for i in range(16):
        #     if not (board & (0xF << (i * 4))):
        #         empty_count += 1

        # if empty_count <= 4:
        #     return constants.DEPTH + 2
        # else:
        #     return constants.DEPTH
        return constants.DEPTH

    def get_best_move(self, board):
        best_move, max_score = -1, -float("inf")

        current_depth = self.get_dynamic_depth(board)

        for d in range(4):
            nb = self.logic.move(board, d)
            if nb != board:
                score = self.expectiminimax(nb, current_depth, False)
                if score >= max_score:
                    max_score, best_move = score, d
        return best_move
