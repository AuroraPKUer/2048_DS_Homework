import pygame
import constants


class Drawer:
    def __init__(self, screen):
        self.screen = screen
        # 修复 Python 3.13 兼容性问题：使用 None 代替 "arial"
        # None 会加载 Pygame 自带的默认字体，避免扫描系统注册表
        self.font_big = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 24)

    def draw_board(self, board, last_move, last_time):
        self.screen.fill((250, 248, 239))

        # 顶部文字
        info = f"AI Move: {last_move} | Speed: {last_time:.3f}s"
        txt = self.font_small.render(info, True, constants.COLORS["text_dark"])
        self.screen.blit(txt, (20, 20))

        # 背景板
        bg_rect = pygame.Rect(
            constants.GAP,
            constants.BOARD_OFFSET_Y,
            constants.WIDTH - 2 * constants.GAP,
            constants.WIDTH - 2 * constants.GAP,
        )
        pygame.draw.rect(self.screen, constants.COLORS["bg"], bg_rect, border_radius=10)

        for i in range(16):
            r, c = i // 4, i % 4
            val_idx = (board >> (i * 4)) & 0xF
            val = 2**val_idx if val_idx > 0 else 0
            x = (
                constants.GAP
                + c * (constants.TILE_SIZE + constants.GAP)
                + constants.GAP
            )
            y = (
                constants.BOARD_OFFSET_Y
                + r * (constants.TILE_SIZE + constants.GAP)
                + constants.GAP
            )

            # 方块颜色
            pygame.draw.rect(
                self.screen,
                constants.COLORS.get(val, (60, 58, 50)),
                (x, y, constants.TILE_SIZE, constants.TILE_SIZE),
                border_radius=5,
            )

            if val > 0:
                color = (
                    constants.COLORS["text_dark"]
                    if val <= 4
                    else constants.COLORS["text_light"]
                )
                # 修复此处：根据数值大小动态调整字体
                font_size = 40 if val < 1000 else 30
                temp_font = pygame.font.Font(None, font_size)
                t = temp_font.render(str(val), True, color)
                self.screen.blit(
                    t,
                    t.get_rect(
                        center=(
                            x + constants.TILE_SIZE / 2,
                            y + constants.TILE_SIZE / 2,
                        )
                    ),
                )

        pygame.display.flip()
