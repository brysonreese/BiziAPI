# /run.py
from src.app import create_app, socketio

if __name__ == '__main__':
    app = create_app()
    # run app
    socketio.run(app, host='0.0.0.0', port=5000)
    ##app.run(host='0.0.0.0', port=5000)