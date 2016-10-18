#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
import random

async def get_message(loop, name, persistent):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 14141, loop=loop
    )
    writer.write(json.dumps({
        'type': 'command',
        'command': 'read',
        'destination': name.rstrip(),
        'persistent_queue': persistent
    }).encode('utf-8'))
    writer.write_eof()
    await writer.drain()
    response = await reader.read()
    writer.close()
    return response

async def get_destination_name():
    path = Path("free_users.txt")
    if path.is_file():
        with open("free_users.txt", 'r+') as f:
            all_names = f.readlines()
            length = len(all_names)
            f.seek(0)
            for i, val in enumerate(all_names):
                if i == 0:
                    name = val
                else:
                    f.write(val)
            f.truncate()
            f.close()
        with open("connected_users.txt", "a") as f:
            f.write(name)
    return name

async def run_receiver(loop):
    name = await get_destination_name()
    int_number = random.randint(1, 2)
    persistent = False
    if int_number == 1:
        persistent = True
    print(persistent)
    while True:
        try:
            response = await get_message(loop, name, persistent)
            print('Received %s', response)
            await asyncio.sleep(2)
        except KeyboardInterrupt:
            break


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_receiver(loop))


if __name__ == '__main__':
    main()
