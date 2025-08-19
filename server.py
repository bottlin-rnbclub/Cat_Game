from flask import Flask, jsonify, request, render_template
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random
import time

app = Flask(__name__)
Base = declarative_base()
engine = create_engine('sqlite:///cats_game.db', echo=True)
Session = sessionmaker(bind=engine)

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    telegram_id = Column(Integer)
    pos_x = Column(Float, default=0)
    pos_y = Column(Float, default=0)
    target_x = Column(Integer, default=0)
    target_y = Column(Integer, default=0)
    score = Column(Integer, default=0)
    join_time = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)

class Coin(Base):
    __tablename__ = 'coins'
    
    id = Column(Integer, primary_key=True)
    pos_x = Column(Integer)
    pos_y = Column(Integer)

Base.metadata.create_all(engine)

def create_coin():
    session = Session()
    session.query(Coin).delete()
    players = session.query(Player).all()
    occupied_positions = [(p.target_x, p.target_y) for p in players]
    while True:
        x, y = random.randint(0, 19), random.randint(0, 14)
        if (x, y) not in occupied_positions:
            coin = Coin(pos_x=x, pos_y=y)
            session.add(coin)
            session.commit()
            break
    session.close()

@app.route('/api/join', methods=['POST'])
def join_game():
    data = request.json
    username = data.get('username')
    telegram_id = data.get('telegram_id')
    
    session = Session()
    player = session.query(Player).filter_by(telegram_id=telegram_id).first()
    if not player:
        x, y = random.randint(0, 19), random.randint(0, 14)
        player = Player(
            username=username,
            telegram_id=telegram_id,
            pos_x=x,
            pos_y=y,
            target_x=x,
            target_y=y,
            score=0,
            join_time=datetime.now(),
            last_active=datetime.now()
        )
        session.add(player)
        session.commit()
    if not session.query(Coin).first():
        create_coin()
    
    session.close()
    return jsonify({'status': 'success', 'x': player.pos_x, 'y': player.pos_y})

@app.route('/api/move', methods=['POST'])
def move_player():
    data = request.json
    telegram_id = data.get('telegram_id')
    direction = data.get('direction')
    
    session = Session()
    player = session.query(Player).filter_by(telegram_id=telegram_id).first()
    if not player:
        session.close()
        return jsonify({'status': 'error', 'message': 'Player not found'})
    new_x, new_y = player.target_x, player.target_y
    if direction == 'up' and player.target_y > 0:
        new_y -= 1
    elif direction == 'down' and player.target_y < 14:
        new_y += 1
    elif direction == 'left' and player.target_x > 0:
        new_x -= 1
    elif direction == 'right' and player.target_x < 19:
        new_x += 1
    
    player.target_x = new_x
    player.target_y = new_y
    player.last_active = datetime.now()
    session.commit()
    
    session.close()
    return jsonify({'status': 'success'})

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    session = Session()
    players = session.query(Player).all()
    coin = session.query(Coin).first()
    if not coin:
        create_coin()
        coin = session.query(Coin).first()
    for player in players:
        if (player.target_x == coin.pos_x and player.target_y == coin.pos_y and
            abs(player.pos_x - player.target_x) < 0.1 and
            abs(player.pos_y - player.target_y) < 0.1):
            
            player.score += 1
            session.commit()
            create_coin()
            coin = session.query(Coin).first()
            break
    players_data = [{
        'username': p.username,
        'x': p.pos_x,
        'y': p.pos_y,
        'target_x': p.target_x,
        'target_y': p.target_y,
        'score': p.score
    } for p in players]
    
    coin_data = {
        'x': coin.pos_x,
        'y': coin.pos_y
    } if coin else None
    
    session.close()
    return jsonify({
        'players': players_data,
        'coin': coin_data
    })

@app.route('/api/update_positions', methods=['POST'])
def update_positions():
    session = Session()
    players = session.query(Player).all()
    for player in players:
        if abs(player.pos_x - player.target_x) > 0.05:
            player.pos_x += 0.05 if player.target_x > player.pos_x else -0.05
        else:
            player.pos_x = player.target_x
            
        if abs(player.pos_y - player.target_y) > 0.05:
            player.pos_y += 0.05 if player.target_y > player.pos_y else -0.05
        else:
            player.pos_y = player.target_y
    
    session.commit()
    session.close()
    return jsonify({'status': 'success'})

@app.route('/leaderboard')
def leaderboard():
    session = Session()
    players = session.query(Player).order_by(Player.score.desc()).all()
    leaderboard_data = [{
        'username': p.username,
        'score': p.score,
        'play_time': (datetime.now() - p.join_time).total_seconds() // 60
    } for p in players]
    session.close()
    return render_template('leaderboard.html', players=leaderboard_data)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)