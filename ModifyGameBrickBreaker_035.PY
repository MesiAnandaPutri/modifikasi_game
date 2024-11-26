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
