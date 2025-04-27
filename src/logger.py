import logging
from logging.handlers import RotatingFileHandler

# File logger setup
def setup_logger():
    logger = logging.getLogger("stockapp")
    logger.setLevel(logging.INFO)
    fh = RotatingFileHandler("logs/stockapp.log", maxBytes=int(5e6), backupCount=5)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger

# Slack handler setup
try:
    from slack_sdk import WebClient
    from logging import Handler

    class SlackHandler(Handler):
        def __init__(self, webhook_url, channel):
            super().__init__(level=logging.ERROR)
            self.client = WebClient()
            self.webhook = webhook_url
            self.channel = channel

        def emit(self, record):
            msg = self.format(record)
            self.client.chat_postMessage(channel=self.channel, text=msg)

    def add_slack(logger, url, channel):
        sh = SlackHandler(url, channel)
        sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(sh)
except ImportError:
    def add_slack(logger, url, channel):
        pass  # Slack not available 