import tkinter as tk
import random
import time

# --- 移动端尺寸适配优化 ---
GAME_WIDTH = 400
GAME_HEIGHT = 450
TANK_SIZE = 26
BULLET_SIZE = 6
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 7
GAME_TIME_LIMIT = 60
TOTAL_ENEMIES = 4

class Bullet:
    def __init__(self, canvas, x, y, direction, owner):
        self.canvas = canvas
        self.direction = direction
        self.owner = owner
        color = "yellow" if owner == 'player' else "orange"
        self.x = x
        self.y = y
        self.id = canvas.create_oval(
            x - BULLET_SIZE // 2, y - BULLET_SIZE // 2,
            x + BULLET_SIZE // 2, y + BULLET_SIZE // 2,
            fill=color, outline=""
        )

    def move(self):
        dx, dy = 0, 0
        if self.direction == 'Up': dy = -BULLET_SPEED
        elif self.direction == 'Down': dy = BULLET_SPEED
        elif self.direction == 'Left': dx = -BULLET_SPEED
        elif self.direction == 'Right': dx = BULLET_SPEED
        
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > GAME_WIDTH or self.y < 0 or self.y > GAME_HEIGHT

class Tank:
    def __init__(self, canvas, x, y, color, speed, is_player=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.direction = 'Up'
        self.is_player = is_player
        self.is_alive = True
        
        self.body_id = canvas.create_rectangle(
            x - TANK_SIZE//2, y - TANK_SIZE//2,
            x + TANK_SIZE//2, y + TANK_SIZE//2,
            fill=color, outline="white" if is_player else "black"
        )
        self.gun_id = canvas.create_line(x, y, x, y - TANK_SIZE//2 - 4, fill="black", width=3)

    def move(self, direction):
        if not self.is_alive: return
        self.direction = direction
        dx, dy = 0, 0
        if direction == 'Up': dy = -self.speed
        elif direction == 'Down': dy = self.speed
        elif direction == 'Left': dx = -self.speed
        elif direction == 'Right': dx = self.speed

        new_x = self.x + dx
        new_y = self.y + dy
        half = TANK_SIZE // 2

        if half <= new_x <= GAME_WIDTH - half and half <= new_y <= GAME_HEIGHT - half:
            self.x = new_x
            self.y = new_y
            self.canvas.move(self.body_id, dx, dy)

        self.update_gun_position()

    def update_gun_position(self):
        gx, gy = self.x, self.y
        offset = TANK_SIZE // 2 + 4
        if self.direction == 'Up': gy -= offset
        elif self.direction == 'Down': gy += offset
        elif self.direction == 'Left': gx -= offset
        elif self.direction == 'Right': gx += offset
        self.canvas.coords(self.gun_id, self.x, self.y, gx, gy)

    def shoot(self):
        if not self.is_alive: None
        owner = 'player' if self.is_player else 'enemy'
        return Bullet(self.canvas, self.x, self.y, self.direction, owner)

    def destroy(self):
        self.is_alive = False
        self.canvas.delete(self.body_id)
        self.canvas.delete(self.gun_id)


class TankGameMobile:
    def __init__(self, root):
        self.root = root
        self.root.title("手机版坦克大战")
        self.root.resizable(False, False)

        # 顶端UI信息栏
        self.info_label = tk.Label(
            root, text="", font=("Arial", 12, "bold"), bg="#222222", fg="white", pady=5
        )
        self.info_label.pack(fill=tk.X)

        # 游戏画布（适配手机竖屏）
        self.canvas = tk.Canvas(root, width=GAME_WIDTH, height=GAME_HEIGHT, bg="black")
        self.canvas.pack()

        # 触控按钮面板区
        control_frame = tk.Frame(root, bg="#444444", pady=5)
        control_frame.pack(fill=tk.X)

        # 创建方向和射击虚拟按键
        btn_font = ("Arial", 14, "bold")
        self.btn_up = tk.Button(control_frame, text="↑", font=btn_font, width=4, command=lambda: self.set_direction('Up'))
        self.btn_down = tk.Button(control_frame, text="↓", font=btn_font, width=4, command=lambda: self.set_direction('Down'))
        self.btn_left = tk.Button(control_frame, text="←", font=btn_font, width=4, command=lambda: self.set_direction('Left'))
        self.btn_right = tk.Button(control_frame, text="→", font=btn_font, width=4, command=lambda: self.set_direction('Right'))
        self.btn_fire = tk.Button(control_frame, text="FIRE", font=btn_font, width=6, bg="darkred", fg="white", command=self.fire_bullet)

        # 布局虚拟按键（模拟方向盘手感）
        self.btn_up.grid(row=0, column=1, padx=5, pady=2)
        self.btn_left.grid(row=1, column=0, padx=5, pady=2)
        self.btn_fire.grid(row=1, column=1, padx=5, pady=2)
        self.btn_right.grid(row=1, column=2, padx=5, pady=2)
        self.btn_down.grid(row=2, column=1, padx=5, pady=2)
        
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        # 游戏变量
        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.current_move_dir = 'Up'
        
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []

        # 初始化玩家与敌方坦克
        self.player = Tank(self.canvas, GAME_WIDTH // 2, GAME_HEIGHT - 40, "green", PLAYER_SPEED, is_player=True)

        for i in range(TOTAL_ENEMIES):
            x = random.randint(40, GAME_WIDTH - 40)
            y = random.randint(30, 120)
            enemy = Tank(self.canvas, x, y, "red", ENEMY_SPEED)
            self.enemies.append(enemy)

        # 兼容键盘（如果手机外接了蓝牙键盘也能用）
        self.root.bind("<KeyPress>", self.on_key_press)

        # 启动主循环
        self.game_loop()

    def set_direction(self, direction):
        if self.game_over: return
        self.current_move_dir = direction
        self.player.move(direction)

    def fire_bullet(self):
        if self.game_over: return
        bullet = self.player.shoot()
        if bullet:
            self.player_bullets.append(bullet)

    def on_key_press(self, event):
        if event.keysym in ['Up', 'Down', 'Left', 'Right']:
            self.set_direction(event.keysym)
        elif event.keysym == 'space':
            self.fire_bullet()

    def update_enemies(self):
        for enemy in self.enemies:
            if random.random() < 0.06:
                enemy.direction = random.choice(['Up', 'Down', 'Left', 'Right'])
            enemy.move(enemy.direction)

            if random.random() < 0.025:
                b = enemy.shoot()
                if b:
                    self.enemy_bullets.append(b)

    def update_bullets(self):
        for b in self.player_bullets[:]:
            b.move()
            if b.is_out_of_bounds():
                self.canvas.delete(b.id)
                self.player_bullets.remove(b)

        for b in self.enemy_bullets[:]:
            b.move()
            if b.is_out_of_bounds():
                self.canvas.delete(b.id)
                self.enemy_bullets.remove(b)

    def check_collisions(self):
        # 玩家子弹打中敌人
        for b in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if abs(b.x - enemy.x) < TANK_SIZE // 2 and abs(b.y - enemy.y) < TANK_SIZE // 2:
                    self.canvas.delete(b.id)
                    if b in self.player_bullets: self.player_bullets.remove(b)
                    enemy.destroy()
                    self.enemies.remove(enemy)
                    self.score += 10
                    break

        # 敌人子弹打中玩家
        for b in self.enemy_bullets[:]:
            if abs(b.x - self.player.x) < TANK_SIZE // 2 and abs(b.y - self.player.y) < TANK_SIZE // 2:
                self.player.destroy()
                self.end_game(won=False, reason="被击中，游戏失败！")
                return

    def update_game_status(self):
        if self.game_over: return

        elapsed_time = int(time.time() - self.start_time)
        remaining_time = max(0, GAME_TIME_LIMIT - elapsed_time)

        self.info_label.config(text=f"得分:{self.score} | 剩余时间:{remaining_time}s | 敌军:{len(self.enemies)}")

        if len(self.enemies) == 0:
            self.end_game(won=True, reason="恭喜胜利！消灭所有敌军！")
            return

        if remaining_time <= 0:
            self.end_game(won=False, reason="时间到！任务失败！")
            return

    def end_game(self, won, reason):
        self.game_over = True
        color = "#4CAF50" if won else "#F44336"
        title = "VICTORY" if won else "GAME OVER"

        self.canvas.create_rectangle(50, 150, 350, 300, fill="black", outline=color, width=3)
        self.canvas.create_text(GAME_WIDTH//2, 190, text=title, fill=color, font=("Arial", 26, "bold"))
        self.canvas.create_text(GAME_WIDTH//2, 245, text=reason, fill="white", font=("Arial", 12))

    def game_loop(self):
        if not self.game_over:
            self.update_enemies()
            self.update_bullets()
            self.check_collisions()
            self.update_game_status()

        self.root.after(25, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = TankGameMobile(root)
    root.mainloop()
