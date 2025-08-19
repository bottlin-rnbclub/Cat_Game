import pgzrun
from random import randint
import requests
import time

SERVER_URL = "http://localhost:5000"

# const
WIDTH = 640
HEIGHT = 480
CELL_SIZE = 32
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

class Cat:
    def __init__(self, username, x, y):
        self.username = username
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.score = 0
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.last_update = time.time()
        self.direction = 'right'
        self.is_moving = False
        self.wait_sprites = {
            'down': Actor('wait_down'),
            'left': Actor('wait_left'),
            'right': Actor('wait_right'),
            'up': Actor('wait_up')
        }
        
        self.walk_sprites = {
            'down': [Actor('walk_down_0'), Actor('walk_down_1'), Actor('walk_down_2'), Actor('walk_down_3')],
            'left': [Actor('walk_left_0'), Actor('walk_left_1'), Actor('walk_left_2'), Actor('walk_left_3')],
            'right': [Actor('walk_right_0'), Actor('walk_right_1'), Actor('walk_right_2'), Actor('walk_right_3')],
            'up': [Actor('walk_up_0'), Actor('walk_up_1'), Actor('walk_up_2'), Actor('walk_up_3')]
        }
        
        # Установка начальной позиции
        screen_x = self.x * CELL_SIZE + CELL_SIZE // 2
        screen_y = self.y * CELL_SIZE + CELL_SIZE // 2
        
        for sprite in self.wait_sprites.values():
            sprite.x = screen_x
            sprite.y = screen_y
        
        for direction_sprites in self.walk_sprites.values():
            for sprite in direction_sprites:
                sprite.x = screen_x
                sprite.y = screen_y
        
    def update(self, new_x, new_y, new_target_x, new_target_y, new_score):
        old_x, old_y = self.x, self.y
        self.x = new_x
        self.y = new_y
        self.target_x = new_target_x
        self.target_y = new_target_y
        self.score = new_score
        
        self.is_moving = (abs(self.x - old_x) > 0.01 or abs(self.y - old_y) > 0.01)
        
        now = time.time()
        if self.is_moving:
            if now - self.last_update > self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.last_update = now
        else:
            self.animation_frame = 0
        
        if new_target_x > self.x:
            self.direction = 'right'
        elif new_target_x < self.x:
            self.direction = 'left'
        elif new_target_y > self.y:
            self.direction = 'down'
        elif new_target_y < self.y:
            self.direction = 'up'
        
        screen_x = self.x * CELL_SIZE + CELL_SIZE // 2
        screen_y = self.y * CELL_SIZE + CELL_SIZE // 2
        
        for sprite in self.wait_sprites.values():
            sprite.x = screen_x
            sprite.y = screen_y
        
        for direction_sprites in self.walk_sprites.values():
            for sprite in direction_sprites:
                sprite.x = screen_x
                sprite.y = screen_y
    
    def draw(self):
        if self.is_moving:
            #анимированные спрайты
            current_sprites = self.walk_sprites[self.direction]
            current_sprite = current_sprites[self.animation_frame]
            current_sprite.draw()
            text_x = current_sprite.x
            text_y = current_sprite.y
        else:
            #спрайты для ожидания
            current_sprite = self.wait_sprites[self.direction]
            current_sprite.draw()
            text_x = current_sprite.x
            text_y = current_sprite.y
        
        screen.draw.text(
            self.username,
            (text_x - len(self.username) * 3, text_y - 40),
            color=(255, 255, 255)
        )
        
        screen.draw.text(
            str(self.score),
            (text_x - 5, text_y + 25),
            color=(255, 255, 0)
        )

cats = []
coin_pos = (0, 0)

def update():
    try:
        response = requests.get(f"{SERVER_URL}/api/game_state")
        if response.status_code == 200:
            data = response.json()
            global coin_pos  

            if data['coin']: 
                coin_pos = (data['coin']['x'], data['coin']['y']) 
            global cats 
            current_usernames = [cat.username for cat in cats]
            for player_data in data['players']: 
                 
                 if player_data['username'] in current_usernames:
                    for cat in cats: 
                        if cat.username == player_data['username'] : 
                            cat.update(
                                player_data['x'],

                                player_data['y'],

                                player_data['target_x'],

                                 player_data['target_y'],

                                 player_data['score'] ,
                                 
                            )

                            break
                 else:
                     
                     cats.append( Cat(
                        player_data['username'],
                        player_data['x'],
                        player_data['y']
                                ))
            
            current_usernames = [player_data['username'] for player_data in data['players']]
            cats = [cat for cat in cats if cat.username in current_usernames]
            
            requests.post( f"{SERVER_URL}/api/update_positions")
    
    except requests.exceptions.RequestException as e:
         print(f"Ошибка при получении состояния игры: {e}")

def draw():
    screen.fill( (50, 50, 70) )
    
    for x in range(0, WIDTH, CELL_SIZE):
         screen.draw.line((x, 0), (x, HEIGHT), (80, 80, 80))
    for y in range(0, HEIGHT, CELL_SIZE):
        screen.draw.line((0, y), (WIDTH, y), (80, 80, 80))
    
    screen.draw.filled_circle(
         ( coin_pos[0] * CELL_SIZE + CELL_SIZE // 2, coin_pos[1] * CELL_SIZE + CELL_SIZE // 2),
         CELL_SIZE // 3,
        ( 255, 215, 0 )
    )
    for cat in cats:
      cat.draw()
    screen.draw.text(
        "Используй кота через телеграмм бота",
        ( 10, 10 ),
         color=( 255, 255, 255 ),
        fontsize=20
    )

pgzrun.go()