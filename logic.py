from functools import lru_cache
import constants


class GameLogic:
    @staticmethod
    @lru_cache(maxsize=65536)
    def get_row_info(row):
        """计算一行的移动结果和评分"""
        line = [(row >> (4 * i)) & 0xF for i in range(4)]

        # 启发式组件: 统计空位、总和、单调性
        empty = line.count(0)
        s_sum = sum(float(p) ** 3.5 for p in line if p > 0)

        mono_left, mono_right = 0.0, 0.0
        for i in range(3):
            if line[i] > line[i + 1]:
                mono_left += line[i] ** 4 - line[i + 1] ** 4
            else:
                mono_right += line[i + 1] ** 4 - line[i] ** 4

        # 结果行计算 (左移)
        new_line = [p for p in line if p != 0]
        res_line = []
        i = 0
        while i < len(new_line):
            if i + 1 < len(new_line) and new_line[i] == new_line[i + 1]:
                res_line.append(new_line[i] + 1)
                i += 2
            else:
                res_line.append(new_line[i])
                i += 1
        res_line += [0] * (4 - len(res_line))

        res_row = 0
        for idx, p in enumerate(res_line):
            res_row |= p << (4 * idx)

        # 计算该行部分分
        h_score = (
            constants.EMPTY_WEIGHT * empty
            - constants.MONOTONICITY_WEIGHT * min(mono_left, mono_right)
            - constants.SUM_WEIGHT * s_sum
        )
        return res_row, h_score

    @staticmethod
    def transpose(x):
        res = x & 0xF0F00F0FF0F00F0F
        res |= (x & 0x0000F0F00000F0F0) << 12
        res |= (x & 0x0F0F00000F0F0000) >> 12
        a = res
        res = a & 0xFF00FF0000FF00FF
        res |= (a & 0x00FF00FF00000000) >> 24
        res |= (a & 0x00000000FF00FF00) << 24
        return res

    @staticmethod
    def reverse_row(row):
        return (
            ((row >> 12) & 0xF)
            | ((row >> 4) & 0xF0)
            | ((row << 4) & 0xF00)
            | ((row << 12) & 0xF000)
        )

    def move(self, board, direction):
        """0:up, 1:down, 2:left, 3:right"""
        if direction < 2:
            board = self.transpose(board)
        res_board = 0
        for i in range(4):
            row = (board >> (i * 16)) & 0xFFFF
            if direction % 2 == 1:
                row = self.reverse_row(row)
            moved_row, _ = self.get_row_info(row)
            if direction % 2 == 1:
                moved_row = self.reverse_row(moved_row)
            res_board |= moved_row << (i * 16)
        if direction < 2:
            res_board = self.transpose(res_board)
        return res_board
