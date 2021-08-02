# Flask Socket IO imports
from . import socketio
from flask_socketio import send, emit, join_room, leave_room, close_room, disconnect, rooms
# Flask imports
from flask import request
# Database models imports
from .models import db, cyberside_user, cyberside_game
from .routes import session
# Flask-Login imports
import flask_login
#Import OS
import os
#Import time
from datetime import datetime,timedelta
import string
import random


# Note that in repl the games will be laggy because the servers are in either europe or us!


# GAME SECTION SOCKETS
# Socket IO connect handler
@socketio.on('connect_game')
def handle_connect(msg):
	if flask_login.current_user.is_authenticated:
		print(f"{flask_login.current_user} : {flask_login.current_user.username} has connected to the game chat with session id {request.sid}")
	flask_login.current_user._session_id = request.sid
	db.session.commit()
	if 'chatID' not in session:
		session['chatID'] = "general_game"
		join_room(session['chatID'])
	elif session['chatID'] == "general":
		leave_room(session['chatID'])
		session['chatID'] = "general_game"
		join_room(session['chatID'])
	elif curr_chat := cyberside_chat.query.filter_by(string_id = session['chatID']).first():
		leave_room(session['chatID'])
		session['chatID'] = "general_game"
		join_room(session['chatID'])
	else:
		leave_room("general_game")	
		join_room(session['chatID'])
		
# Socket IO disconnect handler
@socketio.on('disconnect_game')
def handle_disconnect(msg):
	if flask_login.current_user.is_authenticated:
		print(f"{flask_login.current_user} : {flask_login.current_user.username} has disconnected from the game chat.")
		flask_login.current_user._session_id = None
		db.session.commit()
	# Change back to general chat after user disconnects
	leave_room(session['chatID'])

# Socket IO recive handler
@socketio.on("game_message")
def handle_game_message(msg):
	refined_msg = msg.split(" ")

	# Command Structure
	if refined_msg[0][0] == "/":
		# Whisper Messages:
		if refined_msg[0] == "/w":
			if len(refined_msg) >= 3:
				message = msg[len(refined_msg[0]) + len(refined_msg[1]) + 2:]
				recipient = cyberside_user.query.filter_by(username = refined_msg[1]).first()
				if recipient:
					if recipient != flask_login.current_user:
						if recipient._session_id:
							emit("private_message", f"{flask_login.current_user.username} : {message}", room=recipient._session_id)
							emit("private_message", f"To {recipient.username} : {message}", room=flask_login.current_user._session_id)
						else:
							emit('private_message', f"User : {recipient.username} is not online!")
					else:
						emit('private_message', f"Can't message yourself!")
				else:
					emit('private_message', f"User : {refined_msg[1]} does not exist!")
			else:
				emit('private_message', "Invalid /w format! Try: /w [user] [message]")
		
		# TTS Messages:
		elif refined_msg[0] == "/tts":
			if len(refined_msg) >= 2:
				message = msg[len(refined_msg[0])+ 1:]
				curr_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
				message = f"{curr_time} | {flask_login.current_user.username} : {message}"
				emit("announce_message", message, room=session['chatID'])
			else:
				emit('private_message', "Invalid /tts format! Try: /tts [message]")

		# Inv A Player:
		elif 'currgame' in session and 'startedgame' not in session and (refined_msg[0] == "/inv" or refined_msg[0] == "/invite"):
			if curr_game := cyberside_game.query.filter_by(string_id = session['chatID']).first():
				if flask_login.current_user.id == curr_game.owner_id:
					if len(refined_msg) >= 2:
						name = msg[len(refined_msg[0])+ 1:]
						if toinv := cyberside_user.query.filter_by(username = name).first():
							if toinv != flask_login.current_user:
								if toinv._session_id:
									if session['currgame'] == 'pong' or session['currgame'] == 'tictactoe' or session['currgame'] == 'achtung':
										if toinv._balance >= 5:
											join_request = f"{flask_login.current_user.username} | {session['currgame']} | {session['chatID']}"
											emit("join_request", join_request, room = toinv._session_id)

										else:
											emit('private_message', f"User : {toinv.username} can't afford to play!")
								else:
									emit('private_message', f"User : {toinv.username} is not online!")
							else:
								emit('private_message', f"Can't invite yourself!")
						else:
							emit('private_message', f"Invalid User : {name} !")
					else:
						emit('private_message', "Invalid /inv format! Try: /inv [name]")
				else:
					emit('private_message', "Only the host can invite players!")


		# Balance Command:
		elif refined_msg[0] == "/bal" or refined_msg[0] == "/balance":
			emit("private_message", f"You have {flask_login.current_user._balance} bullets")

		# Help Command:		
		elif refined_msg[0] == "/help" or refined_msg[0] == "/?":
			permissions = "/help ; /? ; /bal ; /balance ; /w ; /tts ; /inv ; /invite"
			emit("private_message", permissions)
			
		# Invalid Command:
		
		else:
			emit('private_message', f"Invalid Command {refined_msg[0]}, try /help!")

	# Regular Messages:
	elif msg:
		if flask_login.current_user.is_authenticated:
			if "chatID" in session:
					curr_time = (datetime.now() + timedelta(hours=3)).strftime('%H:%M')
					formated_msg = f"{curr_time} | {flask_login.current_user.username} : {msg}"
					emit("game_message", formated_msg, room=session['chatID'])

@socketio.on("game_win")
def handle_game_won():
	flask_login.current_user._balance += 10
	# session['bullets'] = flask_login.current_user._balance
	db.session.commit()

@socketio.on("game_start")
def handle_game_started(msg):
	session['startedgame'] = True

@socketio.on("game_player_position")
def handle_game_position(msg):
	if curr_game := cyberside_game.query.filter_by(string_id = session['chatID']).first():
		i = 1
		for member in curr_game.user_list:
			if member._session_id:
				emit("game_player_position", i ,room=member._session_id)
				i += 1

@socketio.on("game_exit")
def handle_game_started(msg):
	session.pop('currgame', None) # Choose game
	session.pop('startedgame', None) # Start game
	if curr_game := cyberside_game.query.filter_by(string_id = session['chatID']).first():
		if flask_login.current_user in curr_game.user_list:
			if flask_login.current_user.id == curr_game.owner_id:
				db.session.delete(curr_game)
			else:
				curr_game.user_list.remove(flask_login.current_user)
				emit("game_message", f"{flask_login.current_user.username} has left the game!" ,room=session['chatID'])
			db.session.commit()
			leave_room(session['chatID'])
			session['chatID'] = "general_game"
			join_room(session['chatID'])

@socketio.on("game_update")
def handle_game_update(cmd):
	if curr_game := cyberside_game.query.filter_by(string_id = session['chatID']).first():
		emit("game_update", cmd, room=session['chatID'])
	
@socketio.on("score_update")
def handle_score_update(cmd):
	if curr_game := cyberside_game.query.filter_by(string_id = session['chatID']).first():
		emit("score_update", cmd, room=session['chatID'])
	

# Socket IO change chat handler
@socketio.on('join_private_game')
def recv_private_chatname(msg):
	msg = msg.split("|")
	cid = msg[0][1:]
	if cid != "general_game":
		if curr_game := cyberside_game.query.filter_by(string_id = cid).first():
			if flask_login.current_user not in curr_game.user_list:
				if msg[1][1:-1] == "pong":
					flask_login.current_user._balance -= 5
					session['bullets'] = flask_login.current_user._balance

				elif msg[1][1:-1] == "breakout":
					flask_login.current_user._balance -= 5
					session['bullets'] = flask_login.current_user._balance

				elif msg[1][1:-1] == "tictactoe":
					flask_login.current_user._balance -= 5
					session['bullets'] = flask_login.current_user._balance
			
				elif msg[1][1:-1] == "achtung":
					flask_login.current_user._balance -= 5
					session['bullets'] = flask_login.current_user._balance
			
				curr_game.user_list.append(flask_login.current_user)
				leave_room(session['chatID'])
				session['chatID'] = cid
				join_room(session['chatID'])
				if len(msg[1][1:-1]) > 0:
					session['currgame'] = msg[1][1:-1]

				emit("game_message", f"{flask_login.current_user.username} has joined the game!", room=session['chatID'])
				emit("player_joined",flask_login.current_user.username, room = session['chatID'])

@socketio.on("allow_start")
def handle_allow_start(msg):
	if curr_game := cyberside_game.query.filter_by(string_id=session['chatID']).first():
		if flask_login.current_user in curr_game.user_list:
			if flask_login.current_user.id == curr_game.owner_id:
				if session['currgame'] == "pong" or session['currgame'] == "tictactoe":
					length = 0
					for member in curr_game.user_list:
						length += 1
					if length == 2:
						emit('allow_start', "true", room=session['chatID'])
					else:
						emit('private_message', f"Insufficient Players! {length}/2, try /inv [name]!")
				elif session['currgame'] == "achtung":
					length = 0
					for member in curr_game.user_list:
						length += 1
					if length == 4:
						emit('allow_start', "true", room=session['chatID'])
					else:
						emit('private_message', f"Insufficient Players! {length}/4, try /inv [name]!")				

				else:
					emit('allow_start', "true", room=session['chatID'])
			else:
				emit('private_message', f"Only the host can start the game!")

@socketio.on("request_players")
def handle_request_players():
	if curr_game := cyberside_game.query.filter_by(string_id=session['chatID']).first():
		for member in curr_game.user_list:
			if member.id == curr_game.owner_id:
				emit("player_joined",member.username + " (HOST)", room = flask_login.current_user._session_id)
			else:
				emit("player_joined",member.username, room = flask_login.current_user._session_id)
