import asyncio
import os
import time
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from .helpers import app_logger
from .messaging import mass_message
from .settings import (
    ANNOUNCEMENTS_SUBFORUM,
    DISCORD_WEBHOOK_FILE,
    POLLING_INTERVAL,
    SERVER_STATUS_FILE,
    TITLE_PAGE,
    TG_ID_FILE,
    RUN_DATA_PATH,
    UP_MESSAGE
)

def get_recent_topic():
    topics = []
    try:
        response = requests.get(ANNOUNCEMENTS_SUBFORUM, timeout=30)
    except Exception as requests_error:
        app_logger.warn(str(requests_error))
        app_logger.warn('Failed to fetch recent topic, retrying....')
        return None
    soup = BeautifulSoup(response.text, "html.parser")

    # Get topics from "Announcements" page 1
    for elem in soup.find_all('dt'):
        '''
        Split lines under topic objects and extract title and creation date
        Original data looks something like this:
        [
            'Game Development: Ancestral Ropewalk\n\n1 ...
            13, 14, 15by jorb » Sun Oct 17, 2021 9:28 pm\n\t\t\t\t'
        ]
        '''
        topic_info = elem.get_text().split('\n')
        topic_title, topic_date = str(topic_info[0]), topic_info[-2:-1]

        # Skip two sections headers
        if topic_title in ['Announcements', 'Topics']:
            continue

        # Get the first <a href> value from dt object
        topic_link = elem.find_all('a')[0].get('href')
        # Strip useless 'sid' value & remove '.' at the beginning
        topic_link = str(topic_link.split('&sid=')[0])[1:]

        # Parse date into datetime format
        topic_date = topic_date[0].split("» ")[-1]
        topic_date = datetime.strptime(topic_date, "%a %b %d, %Y %I:%M %p")
        topics.append([topic_title, topic_date, topic_link])
    if not topics:
        return None
    # Iterate over dates and find the most recent one. Write topic name & date into new var
    recent_topic = [x for x in topics if x[1] == max([x[1] for x in topics])][0]

    return recent_topic


def get_server_status():
    try:
        response = requests.get(TITLE_PAGE, timeout=30)
    except Exception as requests_error:
        app_logger.warn(str(requests_error))
        app_logger.warn('Failed to fetch server status, retrying....')
        return None

    # Scrape server status
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        server_status = soup.find(id = "status").find('h2').get_text()
    except Exception as parse_error:
        app_logger.warn(str(parse_error))
        app_logger.warn(f'Server Response - {response.text}')
        server_status = None

    return server_status


def run_data_check():
    # Check run_data directory and all files. Create them if needed
    if not os.path.isdir(RUN_DATA_PATH):
        os.makedirs(RUN_DATA_PATH)

    if not os.path.isfile(f'{RUN_DATA_PATH}/{TG_ID_FILE}'):
        open(f'{RUN_DATA_PATH}/{TG_ID_FILE}', 'w').close()
    if not os.path.isfile(f'{RUN_DATA_PATH}/{DISCORD_WEBHOOK_FILE}'):
        open(f'{RUN_DATA_PATH}/{DISCORD_WEBHOOK_FILE}', 'w').close()
    if not os.path.isfile(f'{RUN_DATA_PATH}/{SERVER_STATUS_FILE}'):
        open(f'{RUN_DATA_PATH}/{SERVER_STATUS_FILE}', 'w').close()


def write_server_status(server_status, recent_topic_date):
    with open(f'{RUN_DATA_PATH}/{SERVER_STATUS_FILE}', 'w') as status_file:
        status_file.write(f'{server_status};{recent_topic_date}')


def hh_polling():
    run_data_check()
    while True:
        server_status = get_server_status()
        recent_topic = get_recent_topic()
        if server_status is None or recent_topic is None:
            time.sleep(POLLING_INTERVAL)
            continue

        recent_topic_date = recent_topic[1]

        # In case server status file was just created - write data to it and skip cycle
        if os.stat(f'{RUN_DATA_PATH}/{SERVER_STATUS_FILE}').st_size == 0:
            write_server_status(server_status, str(recent_topic_date))
            time.sleep(POLLING_INTERVAL)
            continue

        with open(f'{RUN_DATA_PATH}/{SERVER_STATUS_FILE}', 'r') as status_file:
            server_data = status_file.readline()
        previous_server_status, previous_topic_date = server_data.split(";")
        previous_topic_date = datetime.strptime(previous_topic_date, '%Y-%m-%d %H:%M:%S')

        # If the current server status differs from previous one - trigger messaging
        if ((UP_MESSAGE not in previous_server_status and UP_MESSAGE in server_status) or
            (UP_MESSAGE not in server_status and UP_MESSAGE in previous_server_status)):
            app.helpers.app_logger.info(f'Server switched status, new status - {server_status}')
            write_server_status(server_status, str(recent_topic_date))
            asyncio.run(mass_message(message_data = server_status))

        # If there is a newer forum topic - trigger messaging
        if recent_topic_date > previous_topic_date:
            write_server_status(server_status, str(recent_topic_date))
            asyncio.run(mass_message(message_data = recent_topic))

        time.sleep(POLLING_INTERVAL)
