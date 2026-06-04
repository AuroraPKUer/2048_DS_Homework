import time
import random
from logic import GameLogic
from ai import AI


class AI_Benchmark:
    def __init__(self):
        self.logic = GameLogic()
        self.ai = AI()
        self.stats = {
            "total_games": 0,
            "win_count": 0,
            "max_tiles": {},
            "total_score": 0,
        }

    def add_tile(self, board):
        empty = [i for i in range(16) if not (board & (0xF << (i * 4)))]
        if not empty:
            return board
        return board | (
            (1 if random.random() < 0.9 else 2) << (random.choice(empty) * 4)
        )

    def get_board_max_tile(self, board):
        max_val = 0
        for i in range(16):
            val_idx = (board >> (i * 4)) & 0xF
            if val_idx > 0:
                max_val = max(max_val, 2**val_idx)
        return max_val

    def run_simulation(self, num_games=20):
        print(f"开始测试 AI 性能，总计运行 {num_games} 局...")
        start_time = time.time()

        for g in range(num_games):
            board = self.add_tile(self.add_tile(0))

            while True:
                best_move = self.ai.get_best_move(board)
                if best_move != -1:
                    board = self.logic.move(board, best_move)
                    board = self.add_tile(board)
                else:
                    break

            # --- 修正后的字典访问 ---
            max_tile = self.get_board_max_tile(board)
            self.stats["total_games"] += 1

            # 更新统计分布
            self.stats["max_tiles"][max_tile] = (
                self.stats["max_tiles"].get(max_tile, 0) + 1
            )

            if max_tile >= 2048:
                self.stats["win_count"] += 1

            current_win_rate = (
                self.stats["win_count"] / self.stats["total_games"]
            ) * 100
            print(
                f"第 {g+1:3d} 局结束 | 最大方块: {max_tile:5d} | 当前胜率: {current_win_rate:6.2f}%"
            )

        end_time = time.time()
        self.print_report(end_time - start_time)

    def print_report(self, duration):
        print("\n" + "=" * 40)
        print("          AI 测试报告")
        print("=" * 40)
        print(f"测试总耗时: {duration:.2f} 秒")
        print(f"总运行场次: {self.stats['total_games']}")
        print(
            f"2048 达成率: {(self.stats['win_count']/self.stats['total_games'])*100:.2f}%"
        )
        print("-" * 40)
        print("最大方块分布:")
        for tile in sorted(self.stats["max_tiles"].keys(), reverse=True):
            count = self.stats["max_tiles"][tile]
            percentage = (count / self.stats["total_games"]) * 100
            print(f"  {tile:5d}: {count:3d} 次 ({percentage:6.2f}%)")
        print("=" * 40)


if __name__ == "__main__":
    benchmark = AI_Benchmark()
    benchmark.run_simulation(num_games=20)
