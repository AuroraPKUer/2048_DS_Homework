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

        # --- 1. 基础评分与最大值搜索 ---
        for i in range(4):
            row_val = (board >> (i * 16)) & 0xFFFF
            rows.append(row_val)

            # 实时更新全局最大方块数值
            for j in range(4):
                tile = (row_val >> (j * 4)) & 0xF
                if tile > max_val:
                    max_val = tile

            # 累加原有的行/列启发式评分
            score += self.logic.get_row_info(row_val)[1]
            score += self.logic.get_row_info((t_board >> (i * 16)) & 0xFFFF)[1]

        # --- 2. 最大数不在角上的处罚 ---
        # 定义四个角的数值
        corners = [
            (rows[0] & 0xF),  # 左上角 (0,0)
            (rows[0] >> 12) & 0xF,  # 右上角 (0,3)
            (rows[3] & 0xF),  # 左下角 (3,0)
            (rows[3] >> 12) & 0xF,  # 右下角 (3,3)
        ]

        if max_val not in corners:
            # 只有当最大值不在任何一个角时，给予重罚
            score -= getattr(constants, "NOT_IN_CORNER_PENALTY", 20000.0) * max_val

        # --- 3. 空行处罚逻辑 (n=2, 3) ---
        penalty_empty = getattr(constants, "EMPTY_ROW_PENALTY", 50000.0)
        if rows[0] != 0 and rows[1] != 0 and rows[2] == 0:
            score -= penalty_empty
        if rows[0] != 0 and rows[1] != 0 and rows[2] != 0 and rows[3] == 0:
            score -= penalty_empty

        # --- 4. 三行无法合并处罚逻辑 ---
        if rows[0] != 0 and rows[1] != 0 and rows[2] != 0:
            can_merge = False
            # 检查水平合并
            for i in range(3):
                line = [(rows[i] >> (4 * j)) & 0xF for j in range(4)]
                for j in range(3):
                    if line[j] != 0 and line[j] == line[j + 1]:
                        can_merge = True
                        break
                if can_merge:
                    break

            # 检查垂直合并
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
            # 采样降低计算量
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
        # # 统计空位数
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

        # 1. 获取当前局面的动态深度
        current_depth = self.get_dynamic_depth(board)

        for d in range(4):
            nb = self.logic.move(board, d)
            if nb != board:
                # 2. 使用动态深度进行搜索
                score = self.expectiminimax(nb, current_depth, False)
                if score >= max_score:
                    max_score, best_move = score, d
        return best_move
