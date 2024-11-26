import logging
        
class Logger:
    def __init__(self, log_file='app.log', option=2):
        self.logger = logging.getLogger(__name__)
        log_level = self.set_log_level_by_code(option)
        self.logger.setLevel(log_level)
        self.log_file = log_file # Set the log file name
        self.formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
        self.add_file_handler(log_level) # Create a file handler for logging to a file
        self.add_console_handler(log_level) # Create a console handler for logging to the console
        
    def set_log_level_by_code(self, option):
        """Set log level by given option

        Args:
            option: log level option.

        Returns:
            log_level: log mensaje level information.
        """
        if option == 1:
            log_level = logging.DEBUG
        elif option == 2:
            log_level = logging.INFO
        elif option == 3:
            log_level = logging.WARNING
        elif option == 4:
            log_level = logging.ERROR
        elif option == 5:
            log_level = logging.CRITICAL
        else:
            log_level = logging.DEBUG
        return log_level
    
    def set_log_level(self, log_level):
        """Set the logging level for the logger and all its handlers

        Args:
            log_level: log level option.
        """
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)

    def add_file_handler(self, log_level=logging.INFO):
        """Add a file handler to the logger with a specified log file and log level

        Args:
            log_level: log level option.
        """
        file_handler = logging.FileHandler(self.log_file)
        self.add_handler(file_handler, log_level)

    def add_console_handler(self, log_level=logging.INFO):
        """Add a console handler to the logger with a specified log level

        Args:
            log_level: log level option.
        """
        console_handler = logging.StreamHandler()
        self.add_handler(console_handler, log_level)

    def add_handler(self, handler, log_level=logging.INFO):
        """Add a handler to the logger with a specified log level

        Args:
            handler: handler object.
            log_level: log level option.
        """
        handler.setLevel(log_level)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def remove_handlers(self):
        """Remove all handlers from the logger and close them
        """
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()

    def debug(self, msg):
        """Log a debug message

        Args:
            msg: message to log.
        """
        self.logger.debug(msg)

    def info(self, msg):
        """Log an informational message

        Args:
            msg: message to log.
        """
        self.logger.info(msg)

    def warning(self, msg):
        """Log a warning message

        Args:
            msg: message to log.
        """
        self.logger.warning(msg)

    def error(self, msg):
        """Log an error message

        Args:
            msg: message to log.
        """
        self.logger.error(msg)

    def critical(self, msg):
        """Log a critical message

        Args:
            msg: message to log.
        """
        self.logger.critical(msg)
    
# Example usage of the Logger class
if __name__ == "__main__":
    # Create a logger object
    logger = Logger()

    # Log some messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Remove all handlers after logging
    logger.remove_handlers()
