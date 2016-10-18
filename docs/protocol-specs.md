## Description of the `notibroker` protocol

The protocol for the system `notibroker` is based on JSON.
`notibroker` exposes the following commands:

- `send` - send a message to the queue;
- `read` - read a message from the queue;

However, it also should have other types of message:

- `message` - an incoming message (read);
- `error` - an error message (response sent to the client);

Example of the structure for a `notibroker` message:

```json
{
    "type": "command",
    "command": "<send>",
    "destination":"receiver",
    "payload": "<payload>"
}
```
```json
{
    "type": "command",
    "command": "<read>",
    "destination":"receiver",
    "persistent_queue": "<True|False>"
}
```
```json
{
    "type": "response",
    "destination": "receiver",
    "payload": "<payload>"
}
```
```json
{
    "type": "error",
    "destination": "receiver",
    "payload": "<payload>"
}
```

`type` is type of the message. It must be one of the following:
- `command`
- `response`
- `error`

`payload` is payload of sent/received message. For an `error` message, the `payload`
contains some info about the error.

`command` is type of action to be executed by the `notibroker` for the `command` message.
