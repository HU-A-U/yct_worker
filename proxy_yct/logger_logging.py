import logging

from logging.handlers import TimedRotatingFileHandler
class get_log():
    def __init__(self):
        self.loglevel = logging.INFO
    def config_log(self, filename=None):
        logger = logging.getLogger(__name__)
        if not bool(filename):
            return self.config_stream_log(logger)
        else:
            return self.config_file_log(logger, filename)
    def config_file_log(self, logger, filename):
        formatter = logging.Formatter(
            ('%(asctime)s  %(pathname)s %(levelname)s 第%(lineno)d行'
             ' %(message)s'))
        # logging.basicConfig(filename=filename,filemode='r')
        logger.setLevel(self.loglevel)
        ch = logging.StreamHandler()
        ch.setLevel(self.loglevel)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        '''定义文件流'''
        fh = TimedRotatingFileHandler(filename=filename, when='s', interval=1)
        fh.setLevel(self.loglevel)
        fh.setFormatter(formatter)
        fh.suffix = ''
        logger.addHandler(fh)
        return logger

    def config_stream_log(self, logger):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(pathname)s--第%(lineno)d行--%(levelname)s--%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(self.loglevel)
        return logger