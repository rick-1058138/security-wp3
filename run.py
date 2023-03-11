from app import db, app

LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True


if __name__ == "__main__":
    db.create_all()
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)
