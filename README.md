# Cat_Game


### Dependencies

- `Python 3.11`
- `time
  random
  requests
  flask
  sqlite3
  sqlalchemy
  telebot
  pgzero `

### Setup

1. Install `Python 3.7.6`

2. Install and activate the virtual environment
```
pip install virtualenv
```

If you haven't already, clone this project from your fork, and enter the main directory.

```
# on linux/macOS
source env/bin/activate
# on windows
env\bin\activate
```

3. Install all dependencies

```
pip install -r requirements.txt
```

3. Run it

```
python snakes.py
```





# technical task:

Create a game in which players can control cats, but not with regular buttons, but remotely - via a Telegram bot.

The game server videos will have a flask application with a database.

The Telegram bot will perform the actions of the game server user via API.

The pgzero application will receive information from the game server via API and draw cats and coins in the right places. Cats move around a field with conditional cells measuring 32x32 pixels.


# Image 

![Image alt](https://github.com/bottlin-rnbclub/Cat_Game/tree/main/imageForGit/1.png)
