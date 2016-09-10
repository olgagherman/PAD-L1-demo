## Base demo of the first PAD lab

#### Installation
To run this project you need Python>=3.4 (recommended 3.5).
[How to install it?](https://www.python.org/downloads/)

Pip (python package manager) should be installed with Python >= 3.4. However,
if you can't find it, check out [this page](https://pip.pypa.io/en/stable/installing/).

#### Dependencies

This project doesn't have any third-party dependencies. However, if you want to
develop it, it's recommended to install dependencies from `./requirements/local.txt`.
Just execute

`pip install -r requirements/local.txt`

#### Running project

This project have 3 components:
- Message broker;
- Client-producer;
- Client-consumer;

Message broker (`src/manage.py`) listens on `localhost:14141` for messages from clients.

Client-producer (`src/sender.py`) sends each second a message, with randomly generated UUID,  **to** the broker.

Client-consumer (`src/sender.py`) polls each second for a new message **from** the broker.

To run the broker just execute the `manage.py` script

`python3.5 src/manage.py`

To start producer and respectively consumer run

`python3.5 src/sender.py`

and

`python3.5 src/receiver.py`

Those scripts should be run from separated terminals.And they'll provide output
about performed operations.
