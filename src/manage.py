#!/usr/bin/env python3
import logging.config
import sched, time
from notibroker.broker import run_server
from notibroker.handlers import backup_messages


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s | %(asctime)s | %(name)s:%(funcName)s | %(process)d | %(thread)d | %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'notibroker': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
})

if __name__ == '__main__':
    run_server()
    s = sched.scheduler(time.time, time.sleep)
    s.enter(5, 0, backup_messages)
    s.run()
