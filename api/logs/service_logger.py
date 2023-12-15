import logging

# This class is used to log the service's activity.
# The logs are saved in the logs folder.
# The logs are saved in the service.log file.
# The logs are saved in the following format:
#   - Time
#   - Name of the logger
#   - Level of the log
#   - Message

# Logger: A logger is the entry point into the logging system.
# Handlers: Send the log records (created by loggers) to the appropriate destination.
class ServiceLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - (%(filename)s:%(lineno)d) - %(message)s ')
        file_handler = logging.FileHandler('logs/service.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

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


if __name__ == '__main__':
    logger = ServiceLogger()
    logger.info('Info message')
    logger.debug('Debug message')
    logger.error('Error message')
    logger.warning('Warning message')