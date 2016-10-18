import asyncio
import collections
import logging
import json
import copy
from pathlib import Path

LOGGER = logging.getLogger(__name__)
_MESSAGE_QUEUE = dict()

MESSAGE_TYPES = collections.namedtuple(
    'MessageTypes', ('command', 'error', 'response')
)(*('command', 'error', 'response'))
COMMANDS = collections.namedtuple(
    'Commands', ('send', 'read')
)(*('send', 'read'))

BACKUP_INTERVAL = 10

async def handle_command(message):
    command = message.get('command')
    destination = message.get('destination')
    LOGGER.debug('Handling command %s', command)
    if command not in COMMANDS:
        LOGGER.error('Got invalid command %s', command)
        raise ValueError('Invalid command. Should be one of %s' % (COMMANDS,))
    if command == COMMANDS.send:
        payload = message.get('payload')
        #verify if the queue exists
        if _MESSAGE_QUEUE.get(destination) == None:
            _MESSAGE_QUEUE[destination] = collections.deque()
            LOGGER.debug('Created new queue for receiver %s', destination)
        _MESSAGE_QUEUE[destination].append(payload)
        msg = 'OK'
    elif command == COMMANDS.read:
        persistent_queue = message.get('persistent_queue')
        if len(_MESSAGE_QUEUE[destination]) > 0:
            msg = _MESSAGE_QUEUE[destination].popleft()
        else:
            msg = "Queue is empty"
    return {
        'type': MESSAGE_TYPES.response,
        'destination': destination,
        'payload': msg
    }

async def dispatch_message(message):
    message_type = message.get('type')
    command = message.get('command')
    if message_type != MESSAGE_TYPES.command:
        LOGGER.error('Got invalid message type %s', message_type)
        raise ValueError('Invalid message type. Should be %s' % (MESSAGE_TYPES.command,))
    LOGGER.debug('Dispatching command %s', command)
    response = await handle_command(message)
    return response

def backup_messages(loop):
    #import ipdb; ipdb.set_trace()
    #queue = collections.deque(_MESSAGE_QUEUE)
    dictionary = copy.deepcopy(_MESSAGE_QUEUE)
    #queue_size = len(queue)
    LOGGER.debug("Copied queue")
    #list_q = list(queue)
    with open('messages.txt', 'w') as f:
        jsonObj = json.dumps(dictionary, indent = 2)
        f.write(jsonObj)
    loop.call_later(BACKUP_INTERVAL, backup_messages, loop)

async def loading_messages():
    path_file = Path('messages.txt');
    if path_file.is_file():
        with open('messages.txt', 'r') as f:
            data = json.load(f)
        for message in data:
            if message != '':
                _MESSAGE_QUEUE[destination].append(message)
    else:
        LOGGER.error("File does not exist");
