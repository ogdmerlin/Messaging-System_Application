import sys
import os
import logging
from flask import Flask, request, jsonify
from datetime import datetime
from celery.result import AsyncResult
from dotenv import load_dotenv
from celery import Celery

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Celery
celery = Celery('tasks', broker='amqp://ogdmerlin:dyusuf1@3.92.133.203:5672//', backend='rpc://3.92.133.203')

# Update Celery configuration
celery.conf.update(
    result_expires=60,  # Task results will expire 1 minute after being stored
)


# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(log_dir, 'messaging_system.log'),
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Import tasks after Celery initialization
from tasks import send_email, log_time

@app.route('/')
def index():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')

    if sendmail:
        task = send_email.delay(sendmail)
        logging.info(f'Email task queued with task id: {task.id}')
        return jsonify({
            'message': 'Email task has been queued.',
            'task_id': task.id
        }), 200
    elif talktome:
        task = log_time.delay()
        return jsonify({
            'message': 'Current time logged.',
            'task_id': task.id
        }), 200
    else:
        logging.warning('Either sendmail or talktome parameter is required.')
        return 'Either sendmail or talktome parameter is required.', 400

@app.route('/task_status/<task_id>')
def get_task_status(task_id):
    result = AsyncResult(task_id, app=celery)
    if result.successful():
        return jsonify({
            'status': 'SUCCESS',
            'message': 'Task completed successfully'
        }), 200
    elif result.failed():
        return jsonify({
            'status': 'FAILURE',
            'message': 'Task failed'
        }), 400
    else:
        return jsonify({
            'status': 'SUCCESS',
            'message': 'Task completed successfully'
        }), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
