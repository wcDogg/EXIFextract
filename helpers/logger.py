import logging
import logging.config
from pathlib import Path

import configure

#
# Logging config
LOGGING_CONFIG = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'standard': {
      'format': '%(asctime)s : %(threadName)s : %(levelname)s : %(name)s : %(funcName)s : %(message)s',
      'datefmt': '%Y-%m-%d %H:%M:%S'},
    'complete': {
        'format': '%(asctime)s - PID: %(process)d - PNAME: %(processName)s'
                  ' - TID: %(thread)d - TNAME: %(threadName)s'
                  ' - %(levelname)s - %(filename)s - %(message)s'}
  },  # end formatters
  'handlers': {
    'console_handler': {
      'class': 'logging.StreamHandler',
      'level': configure.LOG_CONSOLE_LEVEL,
      'formatter': 'standard',
      'stream': 'ext://sys.stdout'},
    'file_handler_info': {
      'class': 'logging.handlers.RotatingFileHandler',
      'level': 'INFO',
      'formatter': configure.LOG_FORMAT,
      'filename': configure.LOG_PATH_INFO,
      'maxBytes': 10485760,  # 10MB
      'backupCount': 3,
      'encoding': 'utf8',
      'delay': True},
    'file_handler_debug': {
      'class': 'logging.handlers.RotatingFileHandler',
      'level': 'DEBUG',
      'formatter': configure.LOG_FORMAT,
      'filename': configure.LOG_PATH_DEBUG,
      'maxBytes': 10485760,  # 10MB
      'backupCount': 3,
      'encoding': 'utf8',
      'delay': True},
    'file_handler_warn': {
      'class': 'logging.handlers.RotatingFileHandler',
      'level': 'WARNING',
      'formatter': configure.LOG_FORMAT,
      'filename': configure.LOG_PATH_WARN,
      'maxBytes': 10485760,  # 10MB
      'backupCount': 3,
      'encoding': 'utf8',
      'delay': True},
    'file_handler_error': {
      'class': 'logging.handlers.RotatingFileHandler',
      'level': 'ERROR',
      'formatter': configure.LOG_FORMAT,
      'filename': configure.LOG_PATH_ERROR,
      'maxBytes': 10485760,  # 10MB
      'backupCount': 3,
      'encoding': 'utf8',
      'delay': True},
    'file_handler_crit': {
      'class': 'logging.handlers.RotatingFileHandler',
      'level': 'CRITICAL',
      'formatter': configure.LOG_FORMAT,
      'filename': configure.LOG_PATH_CRIT,
      'maxBytes': 10485760,  # 10MB
      'backupCount': 3,
      'encoding': 'utf8',
      'delay': True}
  },  # end handlers
  'loggers': {
    '<Module>': {
      'level': 'DEBUG',
      'handlers': ['console_handler', 'file_handler_info', 'file_handler_debug', 'file_handler_warn',   'file_handler_error', 'file_handler_crit'],
      'propagate': False},
    '<Module.x>': {
      'level': 'DEBUG',
      'handlers': ['console_handler', 'file_handler_info', 'file_handler_debug', 'file_handler_warn',   'file_handler_error', 'file_handler_crit'],
      'propagate': True},
  },  # end loggers
  'root': {
    'level': 'NOTSET',
    # Must attach all file handlers or files will be created but not written.
    'handlers': ['console_handler', 'file_handler_info', 'file_handler_debug', 'file_handler_warn',   'file_handler_error', 'file_handler_crit'],
    'propagate': True  # always True
  },  # end root
}

#
# Run this one time in main()
def setup_logging():
  '''Sets up logging using the LOGGING_CONFIG dictionary.
  '''
  # Create save directory.
  if not Path(configure.LOG_DIR).is_dir():
    try:
      Path(configure.LOG_DIR).mkdir(parents=True, exist_ok=True)

    except Exception as e:
      use_logging_baseconfig()
      logging.error('The log directory could not be created. Console only - no log files will be written.')
      logging.exception(e)            
      return

  # Configure logging.
  try:
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.debug('Successful LOGGING_CONFIG') 
    logging.debug(f'Log file: {configure.LOG_PATH_INFO}') 
    logging.debug(f'Log file: {configure.LOG_PATH_DEBUG}') 
    logging.debug(f'Log file: {configure.LOG_PATH_WARN}') 
    logging.debug(f'Log file: {configure.LOG_PATH_ERROR}')
    logging.debug(f'Log file: {configure.LOG_PATH_CRIT}')
    
  except Exception as e:
    use_logging_baseconfig()
    logging.error('Error in LOGGING_CONFIG. Console only - no log files will be written.')
    logging.exception(e)

#
# Fallback configuration
def use_logging_baseconfig():
  '''If any part of logging configuration fails, use these settings instead.
  '''
  _datetime = LOGGING_CONFIG['formatters']['standard']['datefmt']

  if configure.LOG_FORMAT == 'complete':
    _format = LOGGING_CONFIG['formatters']['complete']['format']
  else:      
    _format = LOGGING_CONFIG['formatters']['standard']['format']

  logging.basicConfig(level = configure.LOG_CONSOLE_LEVEL, format = _format, datefmt = _datetime)

#
# Test
def test_logging():
  '''Test logging configuration by logging a message at every level.
  '''
  logging.info('Test info')
  logging.debug('Test debug')
  logging.warning('Test warn')
  logging.error('Test error')
  logging.critical('Test critical')
