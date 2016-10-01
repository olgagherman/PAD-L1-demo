#!/usr/bin/env python3
import asyncio
import json

async def get_message(loop):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 14141, loop=loop
    )
    writer.write(json.dumps({
        'type': 'command',
        'command': 'read'
    }).encode('utf-8'))
    writer.write_eof()
    await writer.drain()
    response = await reader.read()
    writer.close()
    return response


async def run_receiver(loop):
    while True:
        try:
            response = await get_message(loop)
            print('Received %s', response)
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_receiver(loop))


if __name__ == '__main__':
    main()
