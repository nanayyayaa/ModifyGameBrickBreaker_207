import tkinter as tk
import random
import threading
import math

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

def play_sfx(effect):
    if not HAS_SOUND: return
    def _play():
        try:
            if effect == 'intro':
                for f in [261, 329, 392, 523, 659]: winsound.Beep(f, 100)
            elif effect == 'bounce': winsound.Beep(600, 40)
            elif effect == 'hit': winsound.Beep(1200, 30)
            elif effect == 'break': winsound.Beep(1600, 50)
            elif effect == 'powerup':
                winsound.Beep(800, 80)
                winsound.Beep(1600, 100)
            elif effect == 'shoot': winsound.Beep(2000, 20)
            elif effect == 'explosion': winsound.Beep(100, 150)
            elif effect == 'bad': winsound.Beep(200, 150)
            elif effect == 'levelup':
                for f in [523, 659, 783, 1046]: winsound.Beep(f, 120)
            elif effect == 'lose':
                for f in [300, 250, 200]: winsound.Beep(f, 300)
        except: pass
    threading.Thread(target=_play, daemon=True).start()


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item
    def get_position(self):
        return self.canvas.coords(self.item)
    def move(self, x, y):
        self.canvas.move(self.item, x, y)
    def delete(self):
        self.canvas.delete(self.item)


class Cloud(GameObject):
    def __init__(self, canvas, x, y):
        self.speed = random.uniform(0.3, 0.8)
        color = '#FFFFFF' 
        
        i1 = canvas.create_oval(x, y, x+60, y+40, fill=color, outline='')
        i2 = canvas.create_oval(x+25, y-20, x+75, y+35, fill=color, outline='')
        i3 = canvas.create_oval(x+55, y+5, x+105, y+40, fill=color, outline='')
        self.parts = [i1, i2, i3]
        super(Cloud, self).__init__(canvas, i1)
        
        for p in self.parts:
            self.canvas.tag_lower(p)

    def update(self):
        for p in self.parts:
            self.canvas.move(p, self.speed, 0)
        if self.canvas.coords(self.parts[0])[0] > 650:
            for p in self.parts:
                self.canvas.move(p, -800, random.randint(-20, 20))


class FloatingText(GameObject):
    def __init__(self, canvas, x, y, text, color='#FF1493'):
        self.life = 25 
        item = canvas.create_text(x, y, text=text, font=('Arial', 12, 'bold'), fill=color)
        self.parts = [item]
        super(FloatingText, self).__init__(canvas, item)
    def update(self):
        self.canvas.move(self.item, 0, -2) 
        self.life -= 1
        if self.life <= 0:
            self.delete()
            return False
        return True
    def delete(self):
        for part in self.parts: self.canvas.delete(part)


class Particle(GameObject):
    def __init__(self, canvas, x, y, color):
        self.size = random.randint(3, 6)
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-6, -1) 
        self.life = random.randint(20, 35) 
        item = canvas.create_rectangle(x, y, x + self.size, y + self.size, fill=color, outline='')
        self.parts = [item]
        super(Particle, self).__init__(canvas, item)
    def update(self):
        self.vy += 0.5 
        self.canvas.move(self.item, self.vx, self.vy)
        self.life -= 1
        if self.life <= 0:
            self.delete()
            return False
        return True
    def delete(self):
        for part in self.parts: self.canvas.delete(part)


class Trail(GameObject):
    def __init__(self, canvas, x, y, color):
        self.life = 8
        item = canvas.create_oval(x-8, y-8, x+8, y+8, fill=color, outline='')
        self.parts = [item]
        super(Trail, self).__init__(canvas, item)
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.delete()
            return False
        return True
    def delete(self):
        for part in self.parts: self.canvas.delete(part)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 12
        self.direction = [1, -1]
        self.speed = 5
        self.piercing = False 
        
        self.item = canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill='#5DADE2', outline='')
        self.layer2 = canvas.create_oval(x-self.radius+2, y-self.radius+2, x+self.radius-2, y+self.radius-2, fill='#82C8EA', outline='')
        self.layer3 = canvas.create_oval(x-self.radius+4, y-self.radius+2, x+self.radius-4, y+self.radius-5, fill='#DDF4FF', outline='')
        self.shine = canvas.create_oval(x-self.radius+6, y-self.radius+4, x-self.radius+10, y-self.radius+8, fill='white', outline='')
        
        self.parts = [self.item, self.layer2, self.layer3, self.shine]
        super(Ball, self).__init__(canvas, self.item)

    def move(self, x, y):
        for part in self.parts: self.canvas.move(part, x, y)
    def delete(self):
        for part in self.parts: self.canvas.delete(part)

    def set_fireball(self, active):
        self.piercing = active
        if active:
            self.canvas.itemconfig(self.item, fill='#E74C3C')
            self.canvas.itemconfig(self.layer2, fill='#E67E22')
            self.canvas.itemconfig(self.layer3, fill='#F1C40F')
        else:
            self.canvas.itemconfig(self.item, fill='#5DADE2')
            self.canvas.itemconfig(self.layer2, fill='#82C8EA')
            self.canvas.itemconfig(self.layer3, fill='#DDF4FF')

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        hit_wall = False
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
            hit_wall = True
        if coords[1] <= 0:
            self.direction[1] *= -1
            hit_wall = True
            
        if hit_wall: play_sfx('bounce')
            
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 110
        self.height = 18
        self.ball = None
        self.is_shrunk = False
        self.expr_timer = 0
        
        self.item = canvas.create_rectangle(x - self.width/2, y - self.height/2, x + self.width/2, y + self.height/2, fill='#FFCA3A', outline='') 
        self.mid = canvas.create_rectangle(x - self.width/2 + 2, y - self.height/2 + 2, x + self.width/2 - 2, y + self.height/2, fill='#FFD659', outline='')
        self.top = canvas.create_rectangle(x - self.width/2 + 4, y - self.height/2 + 2, x + self.width/2 - 4, y - self.height/2 + 8, fill='#FFE599', outline='')
        
        self.eye_l = canvas.create_oval(x - 22, y - 3, x - 14, y + 5, fill='#555555', outline='')
        self.eye_r = canvas.create_oval(x + 14, y - 3, x + 22, y + 5, fill='#555555', outline='')
        self.blush_l = canvas.create_oval(x - 32, y + 1, x - 20, y + 7, fill='#FF9999', outline='')
        self.blush_r = canvas.create_oval(x + 20, y + 1, x + 32, y + 7, fill='#FF9999', outline='')
        
        self.mouth = canvas.create_arc(x - 6, y - 2, x + 6, y + 6, start=180, extent=180, style=tk.ARC, outline='#555555', width=2)
        
        self.parts = [self.item, self.mid, self.top, self.eye_l, self.eye_r, self.blush_l, self.blush_r, self.mouth]
        super(Paddle, self).__init__(canvas, self.item)

    def set_ball(self, ball):
        self.ball = ball

    def set_expression(self, expr):
        if expr == 'shocked':
            self.canvas.itemconfig(self.mouth, start=0, extent=359, style=tk.CHORD, fill='#555555', outline='')
            self.expr_timer = 20 
        elif expr == 'smile':
            self.canvas.itemconfig(self.mouth, start=180, extent=180, style=tk.ARC, fill='', outline='#555555')
            
    def update_animation(self):
        if self.expr_timer > 0:
            self.expr_timer -= 1
            if self.expr_timer == 0:
                self.set_expression('smile')

    def shrink(self, active):
        coords = self.get_position()
        cx = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        
        if active and not self.is_shrunk:
            self.width = 60 
            self.is_shrunk = True
        elif not active and self.is_shrunk:
            self.width = 110 
            self.is_shrunk = False
            
        self.canvas.coords(self.item, cx - self.width/2, y - self.height/2, cx + self.width/2, y + self.height/2)
        self.canvas.coords(self.mid, cx - self.width/2 + 2, y - self.height/2 + 2, cx + self.width/2 - 2, y + self.height/2)
        self.canvas.coords(self.top, cx - self.width/2 + 4, y - self.height/2 + 2, cx + self.width/2 - 4, y - self.height/2 + 8)

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            for part in self.parts:
                self.canvas.move(part, offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)
    def delete(self):
        for part in self.parts: self.canvas.delete(part)


class Brick(GameObject):
    COLORS = {
        3: ('#A381A4', '#CBAACB', '#E4CFE4'), 
        2: ('#E59A95', '#FFB7B2', '#FFD6D3'), 
        1: ('#E5B2C0', '#FFD1DC', '#FFEAEE'),
        -1: ('#2C3E50', '#C0392B', '#E74C3C') 
    }

    def __init__(self, canvas, x, y, hits, is_moving=False):
        self.width = 70
        self.height = 25
        self.hits = hits
        self.is_tnt = (hits == -1)
        
        self.is_moving = is_moving
        self.base_x = x
        self.time_step = 0 
        
        c_dark, c_mid, c_light = Brick.COLORS[hits]
        self.current_color = c_mid 
        
        item = canvas.create_rectangle(x - self.width/2, y - self.height/2, x + self.width/2, y + self.height/2, fill=c_dark, outline='white', width=1, tags='brick')
        self.inner = canvas.create_rectangle(x - self.width/2 + 2, y - self.height/2 + 2, x + self.width/2 - 2, y + self.height/2 - 2, fill=c_mid, outline='')
        self.highlight = canvas.create_rectangle(x - self.width/2 + 4, y - self.height/2 + 2, x + self.width/2 - 4, y - self.height/2 + 8, fill=c_light, outline='')
        
        self.parts = [item, self.inner, self.highlight]
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        if self.is_tnt:
            coords = self.get_position()
            self.delete()
            return True, coords, self.current_color, True 

        self.hits -= 1
        if self.hits == 0:
            play_sfx('break')
            coords = self.get_position()
            self.delete()
            return True, coords, self.current_color, False
        else:
            play_sfx('hit')
            c_dark, c_mid, c_light = Brick.COLORS[self.hits]
            self.current_color = c_mid
            self.canvas.itemconfig(self.item, fill=c_dark)
            self.canvas.itemconfig(self.inner, fill=c_mid)
            self.canvas.itemconfig(self.highlight, fill=c_light)
            return False, None, None, False
            
    def update_movement(self):
        if not self.is_moving: return
        self.time_step += 0.04 
        target_x = self.base_x + (math.sin(self.time_step) * 40)
        current_x = self.get_position()[0] + self.width/2
        dx = target_x - current_x
        for part in self.parts:
            self.canvas.move(part, dx, 0)
            
    def delete(self):
        for part in self.parts: self.canvas.delete(part)


class PowerUp(GameObject):
    def __init__(self, canvas, x, y, ptype):
        self.ptype = ptype
        self.speed = 4
        if ptype == 'M': color, text_char = '#AEC6CF', 'M' 
        elif ptype == 'R': color, text_char = '#FFB7B2', 'R' 
        elif ptype == 'F': color, text_char = '#F39C12', 'F' 
        elif ptype == 'T': color, text_char = '#34495E', 'X' 
        elif ptype == 'S': color, text_char = '#76D7C4', 'S'
        
        item = canvas.create_oval(x - 12, y - 12, x + 12, y + 12, fill=color, outline='white', width=2)
        self.label = canvas.create_text(x, y, text=text_char, font=('Arial', 11, 'bold'), fill='white')
        self.parts = [item, self.label]
        super(PowerUp, self).__init__(canvas, item)
    def update(self):
        for part in self.parts: self.canvas.move(part, 0, self.speed)
    def delete(self):
        for part in self.parts: self.canvas.delete(part)


class Rocket(GameObject):
    def __init__(self, canvas, x, y):
        self.speed = -10
        item = canvas.create_rectangle(x - 3, y - 12, x + 3, y + 12, fill='#FF6B6B', outline='white', width=1)
        self.parts = [item]
        super(Rocket, self).__init__(canvas, item)
    def update(self):
        self.canvas.move(self.item, 0, self.speed)
    def delete(self):
        self.canvas.delete(self.item)


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.level = 1 
        self.combo = 1 
        self.width = 610
        self.height = 450
        
        self.canvas = tk.Canvas(self, bg='#FFF0F5', width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.balls, self.powerups, self.rockets = [], [], []
        self.particles, self.trails, self.float_texts, self.clouds = [], [], [], []
        
        self.rocket_timer = 0
        self.fireball_timer = 0
        self.shrink_timer = 0
        self.shield_item = None
        
        self.is_playing = False
        self.is_paused = False
        self.pause_text = None
        
        self.paddle = Paddle(self.canvas, self.width/2, 380)
        self.items[self.paddle.item] = self.paddle
        
        self.hud = None
        self.pressed_keys = {'Left': False, 'Right': False}
        
        for _ in range(8):
            self.clouds.append(Cloud(self.canvas, random.randint(-100, 600), random.randint(20, 350)))
        
        self.build_bricks()
        self.setup_game()
        self.canvas.focus_set()
        
        self.canvas.bind('<KeyPress-Left>', lambda _: self.pressed_keys.update({'Left': True}))
        self.canvas.bind('<KeyRelease-Left>', lambda _: self.pressed_keys.update({'Left': False}))
        self.canvas.bind('<KeyPress-Right>', lambda _: self.pressed_keys.update({'Right': True}))
        self.canvas.bind('<KeyRelease-Right>', lambda _: self.pressed_keys.update({'Right': False}))
        
        self.canvas.bind('<p>', lambda _: self.toggle_pause())
        self.canvas.bind('<Escape>', lambda _: self.toggle_pause())

        play_sfx('intro')

    def update_background_theme(self):
        # Mengubah warna latar belakang (langit) berdasarkan level permainan
        if self.level == 1:
            bg_color = '#FFF0F5' # Pagi / Pink Pastel (Lavender Blush)
        elif self.level == 2:
            bg_color = '#FDEBD0' # Sore / Oranye Hangat (Peach)
        else:
            bg_color = '#E8F8F5' # Malam / Biru Kehijauan Tenang (Mint Pastel)
        self.canvas.config(bg=bg_color)

    def toggle_pause(self):
        if not self.is_playing: return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_text = self.draw_text(self.width/2, self.height/2 + 20, 'Permainan Dijeda\nTekan P atau ESC untuk melanjutkan', size='20')
        else:
            if self.pause_text:
                self.canvas.delete(self.pause_text)
                self.pause_text = None

    def build_bricks(self):
        for x in range(5, self.width - 5, 75):
            for y, hits in [(80, 3), (110, 2), (140, 1)]:
                if random.random() < 0.10: hits = -1 
                is_moving = True if (y <= 110 and self.level > 1) else False
                self.add_brick(x + 37.5, y, hits, is_moving)

    def clear_entities(self):
        for lst in [self.balls, self.powerups, self.rockets, self.particles, self.trails, self.float_texts]:
            for item in lst: item.delete()
            lst.clear()
        if self.shield_item:
            self.canvas.delete(self.shield_item)
            self.shield_item = None
        self.rocket_timer = self.fireball_timer = self.shrink_timer = 0
        self.combo = 1
        self.paddle.shrink(False)
        self.is_playing = False

    def setup_game(self):
           self.update_background_theme() # Update tema warna langit tiap setup level
           self.add_ball()
           self.update_hud_text()
           self.text = self.draw_text(305, 230, 'Tekan Spasi untuk Mulai\nSelamat bermain!', size='18')
           self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        self.clear_entities()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        ball = Ball(self.canvas, x, 355)
        ball.speed = 5 + (self.level - 1) 
        self.balls.append(ball)
        self.paddle.set_ball(ball)

    def add_brick(self, x, y, hits, is_moving=False):
        brick = Brick(self.canvas, x, y, hits, is_moving)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='20'):
        return self.canvas.create_text(x, y, text=text, font=('Comic Sans MS', size, 'bold'), fill='#725178', justify='center')

    def update_hud_text(self):
        text = f'Nyawa: {self.lives}      Skor: {self.score}      Level: {self.level}'
        if self.hud is None:
            self.hud = self.canvas.create_text(20, 20, text=text, anchor='w', font=('Comic Sans MS', 13, 'bold'), fill='#725178')
        else:
            self.canvas.itemconfig(self.hud, text=text)
        self.canvas.tag_raise(self.hud)

    def screen_shake(self, count=10):
        if count > 0 and not self.is_paused:
            dx, dy = random.randint(-4, 4), random.randint(-4, 4)
            sign = 1 if count % 2 == 0 else -1
            self.canvas.move("all", dx * sign, dy * sign)
            self.after(30, lambda: self.screen_shake(count - 1))

    def trigger_explosion(self, x, y):
        play_sfx('explosion')
        self.screen_shake() 
        items = self.canvas.find_overlapping(x-55, y-55, x+55, y+55)
        for item in items:
            if item in self.items and isinstance(self.items[item], Brick):
                obj = self.items[item]
                is_tnt = obj.is_tnt
                destroyed, b_coords, color, _ = obj.hit()
                if destroyed:
                    score_gained = 10 * self.combo
                    self.score += score_gained
                    self.spawn_particles(b_coords, color, count=10)
                    self.float_texts.append(FloatingText(self.canvas, (b_coords[0]+b_coords[2])/2, b_coords[1]-10, f"+{score_gained}"))
                    del self.items[item]
                    if random.random() < 0.3: self.spawn_powerup(b_coords)
                    if is_tnt: 
                        cx = (b_coords[0] + b_coords[2]) / 2
                        cy = (b_coords[1] + b_coords[3]) / 2
                        self.after(100, lambda: self.trigger_explosion(cx, cy))
        self.update_hud_text()

    def spawn_powerup(self, coords):
        x, y = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
        ptype = random.choices(['M', 'R', 'F', 'T', 'S'], weights=[20, 20, 20, 20, 20])[0]
        self.powerups.append(PowerUp(self.canvas, x, y, ptype))
        
    def spawn_particles(self, coords, color, count=5):
        x, y = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
        for _ in range(count):
            self.particles.append(Particle(self.canvas, x, y, color))

    def activate_powerup(self, ptype):
        if ptype == 'T': 
            play_sfx('bad')
            self.shrink_timer = 300 
            self.paddle.shrink(True)
        else:
            play_sfx('powerup')
            if ptype == 'S':
                if not self.shield_item:
                    self.shield_item = self.canvas.create_rectangle(0, self.height-12, self.width, self.height, fill='#76D7C4', outline='white', tags='shield')
            elif ptype == 'M' and self.balls:
                b = self.balls[0]
                coords = b.get_position()
                x, y = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
                for d in [[1, -1], [-1, -1]]:
                    nb = Ball(self.canvas, x, y)
                    nb.speed = b.speed
                    nb.direction = d
                    if b.piercing: nb.set_fireball(True)
                    self.balls.append(nb)
            elif ptype == 'R':
                self.rocket_timer = 300
            elif ptype == 'F':
                self.fireball_timer = 300
                for b in self.balls: b.set_fireball(True)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.is_playing = True
        self.game_loop()

    def game_loop(self):
        if self.is_paused:
            self.after(16, self.game_loop)
            return

        self.paddle.update_animation()

        if self.pressed_keys['Left']: self.paddle.move(-10)
        if self.pressed_keys['Right']: self.paddle.move(10)
        
        for cloud in self.clouds: cloud.update()
            
        for item in self.items.values():
            if isinstance(item, Brick): item.update_movement()

        if self.rocket_timer > 0:
            self.rocket_timer -= 1
            if self.rocket_timer % 15 == 0:
                play_sfx('shoot')
                pc = self.paddle.get_position()
                self.rockets.extend([Rocket(self.canvas, pc[0]+15, pc[1]), Rocket(self.canvas, pc[2]-15, pc[1])])
        
        if self.fireball_timer > 0:
            self.fireball_timer -= 1
            if self.fireball_timer == 0:
                for b in self.balls: b.set_fireball(False)
                
        if self.shrink_timer > 0:
            self.shrink_timer -= 1
            if self.shrink_timer == 0:
                self.paddle.shrink(False)

        for ball in self.balls[:]:
            ball_coords = ball.get_position()
            if ball_coords[3] >= self.height - 12 and self.shield_item:
                ball.direction[1] = -1
                ball.move(0, -15)
                self.canvas.delete(self.shield_item)
                self.shield_item = None
                play_sfx('bounce')
            elif ball_coords[3] >= self.height:
                ball.delete()
                self.balls.remove(ball)
            else:
                self.handle_ball_collisions(ball)
                ball.update()
                color = '#F39C12' if ball.piercing else '#82C8EA'
                self.trails.append(Trail(self.canvas, (ball_coords[0]+ball_coords[2])/2, (ball_coords[1]+ball_coords[3])/2, color))

        for p in self.particles[:]:
            if not p.update(): self.particles.remove(p)
        for t in self.trails[:]:
            if not t.update(): self.trails.remove(t)
        for ft in self.float_texts[:]:
            if not ft.update(): self.float_texts.remove(ft)
            
        for r in self.rockets[:]:
            r.update()
            if r.get_position()[1] <= 0:
                r.delete()
                self.rockets.remove(r)
            else:
                self.handle_rocket_collisions(r)
                
        for pu in self.powerups[:]:
            pu.update()
            c = pu.get_position()
            if c[3] >= self.height:
                pu.delete()
                self.powerups.remove(pu)
            else:
                items = self.canvas.find_overlapping(*c)
                if self.paddle.item in items or self.paddle.mid in items:
                    self.paddle.set_expression('shocked') 
                    self.activate_powerup(pu.ptype)
                    self.score += 25 
                    self.update_hud_text()
                    pu.delete()
                    self.powerups.remove(pu)
