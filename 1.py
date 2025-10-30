import pygame
import math
import random

# 初始化pygame
pygame.init()
pygame.font.init()

# 窗口设置
WIDTH, HEIGHT = 1400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("粒子汇聚爱心与文字")


# 确保中文显示的字体设置
def get_chinese_font(size):
    chinese_fonts = ["SimHei", "Microsoft YaHei", "Heiti TC", "SimSun", "WenQuanYi Micro Hei"]
    for font_name in chinese_fonts:
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            continue
    return pygame.font.Font(None, size)


chinese_font = get_chinese_font(120)

# 颜色方案
COLORS = [
    (255, 99, 71), (255, 165, 0), (255, 105, 97),
    (255, 182, 193), (255, 20, 147), (138, 43, 226)
]


# 粒子类（增大粒子尺寸，优化分布）
class Particle:
    def __init__(self, phase=0):
        # 初始位置
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = 0
        elif edge == 'bottom':
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT
        elif edge == 'left':
            self.x = 0
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT)

        # 粒子属性（适度增大粒子尺寸）
        self.size = random.uniform(1.8, 3)  # 粒子大小调整为1.8-3像素
        self.color = random.choice(COLORS)
        self.speed = random.uniform(1.2, 3.2)
        self.phase = phase
        self.target_idx = random.randint(0, 359)
        self.alpha = 255
        self.arrived = False

    # 爱心轨迹点
    @staticmethod
    def get_love_points():
        points = []
        for angle in range(360):
            t = math.radians(angle)
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            scale = 16
            center_x = WIDTH // 2
            center_y = HEIGHT // 2 - 80
            points.append((center_x + x * scale, center_y + y * scale))
        return points

    # 文字粒子点（优化采样密度适配大粒子）
    @staticmethod
    def get_text_points():
        points = []
        text = "珂珂永远开心"
        char_spacing = 160  # 适当增加字间距，避免大粒子重叠
        start_x = WIDTH // 2 - (char_spacing * (len(text) - 1)) // 2
        y_pos = HEIGHT // 2 + 50

        for i, char in enumerate(text):
            char_surface = chinese_font.render(char, True, (255, 255, 255))
            char_x = start_x + i * char_spacing
            char_rect = char_surface.get_rect(center=(char_x, y_pos))

            # 优化采样间隔，适配大粒子
            for y in range(0, char_rect.height, 2):  # 每2像素采样，避免点过密
                for x in range(0, char_rect.width, 2):
                    if char_surface.get_at((x, y))[3] > 100:
                        points.append((char_rect.x + x, char_rect.y + y))

            # 补充内部点，确保大粒子能填充文字
            for _ in range(250):  # 每个字补充250个点
                x = random.randint(char_rect.x + 15, char_rect.right - 15)
                y = random.randint(char_rect.y + 15, char_rect.bottom - 15)
                points.append((x, y))

        return points

    # 更新位置
    def update(self, love_points, text_points):
        target_points = love_points if self.phase == 0 else text_points
        if self.target_idx >= len(target_points):
            self.target_idx = random.randint(0, len(target_points) - 1)
        target_x, target_y = target_points[self.target_idx]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.arrived = True
            if random.random() < 0.1:
                self.x += random.uniform(-1, 1)  # 适配大粒子的抖动幅度
                self.y += random.uniform(-1, 1)
        else:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

        return True

    # 绘制粒子（适配大粒子的光晕）
    def draw(self, surface):
        if self.arrived:
            # 光晕尺寸随粒子增大
            glow_surf = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (*self.color[:3], 40),  # 适度增强光晕
                (int(self.size * 2), int(self.size * 2)),
                int(self.size * 2)
            )
            surface.blit(glow_surf, (int(self.x - self.size * 2), int(self.y - self.size * 2)))

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


# 主函数（调整粒子数量平衡大粒子）
def main():
    love_points = Particle.get_love_points()
    text_points = Particle.get_text_points()

    # 粒子数量适中，避免大粒子导致的拥挤
    particles = [Particle() for _ in range(3500)]

    bg_alpha = 0
    phase = 0
    phase_timer = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        phase_timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if bg_alpha < 230:
            bg_alpha += 1
        screen.fill((0, 0, 0, bg_alpha), special_flags=pygame.BLEND_RGBA_MULT)

        # 7秒后切换到文字
        if phase_timer > 420 and phase == 0:
            phase = 1
            for p in particles:
                p.phase = 1
                p.arrived = False
                p.target_idx = random.randint(0, len(text_points) - 1)

        for p in particles:
            p.update(love_points, text_points)
            p.draw(screen)

        # 控制粒子补充频率
        if random.random() < 0.5:
            new_particle = Particle(phase=1 if phase >= 1 else 0)
            particles.append(new_particle)
            if len(particles) > 4500:  # 限制最大数量，避免大粒子重叠
                particles.pop(0)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()