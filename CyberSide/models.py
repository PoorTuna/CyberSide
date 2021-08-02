# Flask-Login incorporation import + Flask-SQLALCHEMY database reference
from flask_login import UserMixin
from . import db, login_manager
#This file contains models and login structure for the CyberSide project

# User class & integration with login manager and data base
cyberside_game_association_table = db.Table('user_game',
db.Column('user_id', db.Integer, db.ForeignKey('cyberside_user.id')),
db.Column('game_id', db.String(20), db.ForeignKey('cyberside_game.string_id'))
)

class cyberside_user(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True) # User ID
	username = db.Column(db.String(12), unique = True, nullable=False) # User Nickname
	email = db.Column(db.String(30), unique = True, nullable=False) # User Email Address
	password = db.Column(db.String(128), nullable=False) # User Password
	_balance = db.Column(db.Integer,default = 50) # User amount of money / balance
	_session_id = db.Column(db.String(60), unique = True) # User session id when he connects to the sockets
	background = db.Column(db.String(30), nullable=False, default = "original") # The current theme he is using
	background_list = db.Column(db.String(100), nullable=False, default = "original|") # The list of owned themes
	game_list = db.relationship('cyberside_game', secondary=cyberside_game_association_table, backref=db.backref('user_list', lazy = 'dynamic')) # User game list.

class cyberside_game(db.Model):
	id = db.Column(db.Integer, primary_key = True) # Game ID
	string_id = db.Column(db.String(20), unique = True, nullable=True) # Game StringID (for protection)
	game_name = db.Column(db.String(25), nullable=False) # Game type / name
	owner_id = db.Column(db.Integer, nullable=True) # not really usefull by itself
	curr_players = db.Column(db.Integer,default = 1) # Amount of current players in the lobby / NOT USED AS OF NOW
	max_players = db.Column(db.Integer,default = 1) # Amount of required players to start a game
	hackers = db.Column(db.String(25), nullable=False) # who are the hackers in the game

@login_manager.user_loader
def load_user(user_id): # loads the user in the session
	return cyberside_user.query.get(int(user_id))

