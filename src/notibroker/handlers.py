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

BACKUP_INTERVAL = 5

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
        if destination in _MESSAGE_QUEUE:
            if len(_MESSAGE_QUEUE[destination]) > 0:
                msg = _MESSAGE_QUEUE[destination].popleft()
                if len(_MESSAGE_QUEUE[destination]) == 0 and not message.get('persistent_queue'):
                        _MESSAGE_QUEUE.pop(destination, None)
            else:
                msg = "Queue is empty"
        else:
            msg = "Queue does not exist"
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
    dictionary = dict()
    for i, val in _MESSAGE_QUEUE.items():
        dictionary[i] = list(val)
        LOGGER.debug("Copied queue for receiver %s", i)
    with open('messages.txt', 'w') as f:
        jsonObj = json.dumps(dictionary, indent = 2)
        f.write(jsonObj)
    loop.call_later(BACKUP_INTERVAL, backup_messages, loop)

async def loading_messages():
    path_file = Path('messages.txt');
    if path_file.is_file():
        with open('messages.txt', 'r') as f:
            data = json.load(f)
        for i, queue in data.items():
            _MESSAGE_QUEUE[i] = collections.deque(queue)
    else:
        LOGGER.error("File does not exist");
