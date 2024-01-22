import logging
import logging.config

def logger():
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'normal': {  # the name of formatter
                'format': "[*] Server %(asctime)s %(levelname)s %(ipaddr)s:%(message)s",
                'datefmt':'%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {  # the name of handler
                'class': 'logging.StreamHandler',  # emit to sys.stderr(default)
                'formatter': 'normal', 
            }, # use the above "normal" formatter
            'file': {  # the name of handler
                'class': 'logging.handlers.RotatingFileHandler',  # emit to disk file
                'filename': './log/server.log',  # the path of the log file
                'formatter': 'normal',  # use the above "normal" formatter
                'maxBytes': 1024*1024,
                'backupCount': 3
            },
        },
        'loggers': {
            'logger': {  # the name of logger
                'handlers': ['file'],  # use the above "console1" and "console2" handler
                'level': 'INFO',  # logging level
            },
        },
    }
    logging.config.dictConfig(config=LOGGING)
    logger = logging.getLogger('logger')

    return logger
