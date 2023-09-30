#!/usr/bin/env python3

import logging

import sys
import os.path
from subprocess import Popen, TimeoutExpired
import shlex
import shutil

import time
from datetime import datetime

# Paths
dirname = "/var/www/html"
screenshot_path = os.path.join(dirname, 'inky.png')

# Set up logging
logging.basicConfig(filename='debug.log', format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.DEBUG)
logfile = open('debug.log', 'a')

def log(message):
    logging.info(message)
    print(message)

log('-- DISPLAY SCRIPT START --')

start_time = time.time()
def time_elapsed():
    return f'{round(time.time() - start_time, 2)}s'

# Start Gunicorn process and wait for server to start
log('Starting gunicorn server')

gunicorn_command = f'gunicorn --access-logfile=- --chdir=\'{dirname}\' \'app:app\' --bind=localhost:9000'
gunicorn_process = Popen(shlex.split(gunicorn_command),
    stdout=logfile, stderr=logfile)

time.sleep(2)

# Start Chromium process
log(f'Rendering display to an image with Chromium')

chromium_command = f'chromium-browser --headless --window-size=640,400 --screenshot="{screenshot_path}" "http://127.0.0.1:9000"'
chromium_process = Popen(shlex.split(chromium_command), stdout=logfile, stderr=logfile)

# Wait for Chromium process to finish or kill it
try:
    chromium_process.communicate(timeout=10)
    log('Chromium done, stopping gunicorn server')
except TimeoutExpired:
    logging.warn('Chromium did not quit, killing and stopping gunicorn server')
    chromium_process.kill()

# Send terminate signal to Gunicorm process or kill it
gunicorn_process.terminate()
try:
    gunicorn_process.communicate(timeout=10)
except TimeoutExpired:
    logging.warn('Gunicorn did not quit, killing 💀')
    gunicorn_process.kill()

log(f'Finished rendering image in {time_elapsed()}, writing to display! ✍️')


# Finish up
logfile.close()
log(f'Done in {time_elapsed()}, BYE!')
log('-- DISPLAY SCRIPT END --')
