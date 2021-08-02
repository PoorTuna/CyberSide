import CyberSide # Import package

if __name__ == "__main__":
	CyberSide.db.create_all()
	CyberSide.socketio.run(CyberSide.app, host='0.0.0.0', port=8080, debug=True)