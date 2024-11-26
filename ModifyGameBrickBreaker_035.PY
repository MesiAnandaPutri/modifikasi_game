import tkinter as tk
import random

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

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10 
        self.direction = [1, -1]
        self.speed = 5 #mengatur kecepatan bola
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
        
    def collide(self, game_objects):
        coords = self.get_position()
        x_center = (coords[0] + coords[2]) * 0.5

        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            object_coords = game_object.get_position()

            # Collision with paddle
            if isinstance(game_object, Paddle):
                paddle_center = (object_coords[0] + object_coords[2]) * 0.5
                offset = (x_center - paddle_center) / (game_object.width / 2)
                self.direction[0] = offset  # Adjust horizontal direction
                self.direction[1] = -abs(self.direction[1])  # Ensure upward direction

            # Collision with brick
            elif isinstance(game_object, Brick):
                self.direction[1] *= -1
                game_object.hit()
                
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

class Brick(GameObject):
    COLORS = {1: '#FFB6C1', 2: '#FF8243', 3: '#87CEFA', 4: '#93E9BE', 5: '#FFD1DC'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super().__init__(canvas, item)

    def hit(self):
        # Tambahkan 20 poin setiap kali balok pecah
        game = self.canvas.master  # Mengakses objek game melalui canvas
        game.score += 20  # Menambah skor
        game.update_score_text()  # Memperbarui tampilan skor

        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3
        self.level = 1
        self.score = 0
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle

        self.hud = None
        self.score_text = None  # Menyimpan referensi ke skor
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()  # Memperbarui skor saat permainan dimulai
        self.draw_ball_lane()  # Menambahkan garis lane bola
        self.text = self.draw_text(300, 200, f'Level {self.level}\nPress Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

        
    def draw_ball_lane(self):
        # Menambahkan garis horizontal sebagai lane bola
        lane_y = self.height - 20  # Lokasi garis sedikit di atas dasar
        self.canvas.create_line(0, lane_y, self.width, lane_y, fill='black', width=2)

    def update_score_text(self):
        text = f'Score: {self.score}'
        if self.score_text is None:
            self.score_text = self.draw_text(self.width - 100, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_text, text=text)

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    
    def load_level(self):
        self.clear_bricks()
        if self.level == 1:
            self.create_Pola_Pertama()
        elif self.level == 2:
            self.create_Pola_Kedua()
        elif self.level == 3:
            self.create_Pola_Ketiga()

    def create_Pola_Pertama(self):
        rows = 5
        brick_width = 75
        brick_height = 20
        start_y = 50

        for row in range(rows):
            bricks_in_row = rows - row
            start_x = (self.width - (bricks_in_row * brick_width)) // 2 + brick_width / 2
            for col in range(bricks_in_row):
                x = start_x + col * brick_width
                y = start_y + row * brick_height
                hits = (self.level % 3) + 1
                self.add_brick(x, y, hits)

    def create_Pola_Kedua(self):
        rows = 8
        cols = 8
        brick_width = 75
        brick_height = 20
        start_y = 50

        maze = [
            [1, 1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1],
            [0, 1, 0, 1, 1, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 0],
            [1, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1],
            [1, 1, 0, 1, 1, 0, 0, 1]
        ]

        for row in range(rows):
            for col in range(cols):
                if maze[row][col] == 1:  # Menambahkan balok di posisi yang tidak kosong
                    x = col * brick_width + brick_width / 2
                    y = start_y + row * brick_height
                    hits = (self.level % 3) + 1
                    self.add_brick(x, y, hits)

    
    def create_Pola_Ketiga(self):
        class MovingBrick(Brick):
            def __init__(self, canvas, x, y, hits, direction):
                super().__init__(canvas, x, y, hits)
                self.direction = direction  # Direction: 1 for right, -1 for left
                self.speed = 6  # Kecepatan gerakan

            def update(self):
                coords = self.get_position()
                if coords[0] <= 0 or coords[2] >= self.canvas.winfo_width():
                    self.direction *= -1  # Ubah arah jika mencapai batas layar
                self.move(self.direction * self.speed, 0)  # Gerakkan balok

            def create_moving_bricks(self):
                rows = 5
                cols = 6
                brick_width = 75
                brick_height = 20
                start_y = 50

                for row in range(rows):
                    for col in range(cols):
                        x = col * brick_width + brick_width / 2
                        y = start_y + row * brick_height
                        hits = (self.level % 3) + 1
                        brick = MovingBrick(self.canvas, x, y, hits, random.choice([-1, 1]))
                        self.items[brick.item] = brick

    