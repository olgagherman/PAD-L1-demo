import asyncio
import json
import logging

from .handlers import dispatch_message, backup_messages, BACKUP_INTERVAL

LOGGER = logging.getLogger(__name__)

async def send_error(writer, reason):
    message = {
        'type': 'error',
        'payload': reason
    }
    payload = json.dumps(message).encode('utf-8')
    writer.write(payload)
    await writer.drain()


async def handle_message(reader, writer):
    data = await reader.read()
    address = writer.get_extra_info('peername')

    LOGGER.debug('Recevied message from %s', address)

    try:
        message = json.loads(data.decode('utf-8'))
    except ValueError as e:
        LOGGER.exception('Invalid message received')
        send_error(writer, str(e))
        return

    try:
        response = await dispatch_message(message)
        payload = json.dumps(response).encode('utf-8')
        writer.write(payload)
        await writer.drain()
        writer.write_eof()
    except ValueError as e:
        LOGGER.exception('Cannot process the message. %s')
        send_error(writer, str(e))

    writer.close()

def run_server(hostname='localhost', port=14141, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_message, hostname, port, loop=loop)
    server = loop.run_until_complete(coro)
    loop.call_later(BACKUP_INTERVAL, backup_messages, loop)
    LOGGER.info('Serving on %s', server.sockets[0].getsockname())
    LOGGER.info('Press Ctrl + C to stop the application')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
