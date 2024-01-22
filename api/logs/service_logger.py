import logging
import logging.handlers

class ServiceLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - (%(filename)s:%(lineno)d) - %(message)s ')

        # Create a file handler for the main logger
        file_handler = logging.handlers.RotatingFileHandler('logs/service.log', maxBytes=1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create a file handler for the 'file' logger
        file_logger_handler = logging.handlers.RotatingFileHandler('logs/file.log', maxBytes=1024*1024, backupCount=3)
        file_logger_handler.setFormatter(formatter)

        # Create a logger for the 'file' handler
        file_logger = logging.getLogger('file')
        file_logger.setLevel(logging.DEBUG)
        file_logger.addHandler(file_logger_handler)

    # info: Confirmation that things are working as expected.
    def info(self, message):
        self.logger.info(message)

    # debug: for detailed information, typically of interest only when diagnosing problems.
    def debug(self, message):
        self.logger.debug(message)

    # error: Due to a more serious problem, the software has not been able to perform some function.
    def error(self, message):
        self.logger.error(message)

    # warning: An indication that something unexpected happened, or indicative of some problem in the near future.
    def warning(self, message):
        self.logger.warning(message)