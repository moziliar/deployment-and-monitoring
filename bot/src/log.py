import logging

from configs import config

logging.basicConfig(filename=config.infoLogPath,
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logging.basicConfig(filename=config.warnLogPath,
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARN)

logging.basicConfig(filename=config.errorLogPath,
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
