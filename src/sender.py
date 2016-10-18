#!/usr/bin/env python3
import asyncio
import json
import uuid
from pathlib import Path
import random

async def send_message(message, destination, loop):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 14141, loop=loop
    )
    payload = json.dumps({
        'type': 'command',
        'command': 'send',
        'destination': destination,
        'payload': message
    }).encode('utf-8')

    writer.write(payload)
    writer.write_eof()
    await writer.drain()

    response = await reader.read(2048)
    writer.close()
    return response

async def get_receiver_name():
    path = Path("connected_users.txt")
    if path.is_file():
        with open("connected_users.txt", 'r') as f:
            names = f.readlines()
            length = len(names)
            if length == 0:
                print("THERE'S NO MORE IDS")
                name = '000000'
            else:
                index = random.randint(0, length - 1)
                name = names[index]
    return name.rstrip()

async def run_sender(loop):
    while True:
        destination = await get_receiver_name()
        try:
            message = 'Just sending a random %s' % (uuid.uuid4().hex,)
            print('Sending %s' % (message,))
            response = await send_message(message, destination, loop)
            print('Received %s', response)
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sender(loop))


if __name__ == '__main__':
    main()
