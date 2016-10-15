import asyncio
import collections
import logging
import copy
import json
import os

LOGGER = logging.getLogger(__name__)
#_MESSAGE_QUEUE = asyncio.Queue(loop=asyncio.get_event_loop())
_MESSAGE_QUEUE = collections.deque()

MESSAGE_TYPES = collections.namedtuple(
    'MessageTypes', ('command', 'error', 'response')
)(*('command', 'error', 'response'))
COMMANDS = collections.namedtuple(
    'Commands', ('send', 'read')
)(*('send', 'read'))

BACKUP_INTERVAL = 10

async def handle_command(command, payload):
    LOGGER.debug('Handling command %s, payload %s', command, payload)
    if command not in COMMANDS:
        LOGGER.error('Got invalid command %s', command)
        raise ValueError('Invalid command. Should be one of %s' % (COMMANDS,))
    if command == COMMANDS.send:
        _MESSAGE_QUEUE.append(payload)
        msg = 'OK'
    elif command == COMMANDS.read:
        msg = _MESSAGE_QUEUE.popleft()
    return {
        'type': MESSAGE_TYPES.response,
        'payload': msg
    }

async def dispatch_message(message):
    message_type = message.get('type')
    command = message.get('command')
    if message_type != MESSAGE_TYPES.command:
        LOGGER.error('Got invalid message type %s', message_type)
        raise ValueError('Invalid message type. Should be %s' % (MESSAGE_TYPES.command,))
    LOGGER.debug('Dispatching command %s', command)
    response = await handle_command(command, message.get('payload'))
    return response

def backup_messages(loop):
    #import ipdb; ipdb.set_trace()
    queue = collections.deque(_MESSAGE_QUEUE)
    queue_size = len(queue)
    LOGGER.debug("Copied queue with size %s", queue_size)
    list_q = list(queue)
    with open('messages.txt', 'w') as f:
        jsonObj = json.dumps(list_q, indent = 2)
        f.write(jsonObj)
    loop.call_later(BACKUP_INTERVAL, backup_messages, loop)

async def loading_messages():
    with open('messages.txt', 'r') as f:
        data = json.load(f)
    if data == None:
        print ("Empty file")
    else:
        for message in data:
            if message != '':
                _MESSAGE_QUEUE.append(message)
