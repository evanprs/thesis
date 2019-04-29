import time
from flask import Flask

api = Flask(__name__)

@api.route('/')
def hello_world():
	time.sleep(5)
	return 'Hello world!'

if __name__ == '__main__':
	api.run(host='0.0.0.0')