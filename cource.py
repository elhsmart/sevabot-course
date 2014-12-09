#!/sevabot
# coding=utf-8
"""
    Simple group chat task manager.
    This also serves as an example how to write stateful handlers.
"""

from __future__ import unicode_literals

from threading import Timer
import os
import logging

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode, get_chat_id

logger = logging.getLogger("Cource")

# Set to debug only during dev
logger.setLevel(logging.INFO)

logger.debug("Cource module level load import")

# How long one can work on a task before we give a warning
MAX_TASK_DURATION = 24*60*60

HELP_TEXT = """!cource skype bot help
Commands
------------------------------
!tasks: This help text
Nothnig here for now
"""


class CourceHandler(StatefulSkypeHandler):
    def __init__(self):
        logger.debug("Cource constructed")

    def init(self, sevabot):

        logger.debug("Cource inited")
        self.sevabot = sevabot
        self.status_file = os.path.join(os.path.dirname(__file__), "sevabot-tasks.tmp")

        self.commands = {
            "!tasks": self.help,
            "курс": self.start_task,
        }

        self.reset_timeout_notifier()

    def handle_message(self, msg, status):
        # Skype API may give different encodings
        # on different platforms
        body = ensure_unicode(msg.Body)

        logger.debug("Tasks handler got: %s" % body)

        # Parse the chat message to commanding part and arguments
        words = body.split(" ")
        lower = body.lower()

        if len(words) == 0:
            return False

        # Parse argument for two part command names
        if len(words) >= 2:
            desc = " ".join(words[2:])
        else:
            desc = None

        chat_id = get_chat_id(msg.Chat)

        # Check if we match any of our commands
        for name, cmd in self.commands.items():
            if lower.startswith(name):
                cmd(msg, status, desc, chat_id)
                return True

        return False

    def shutdown(self):
        """ Called when the module is reloaded.
        """
        logger.debug("Tasks shutdown")
        self.stop_timeout_notifier()

    def reset_timeout_notifier(self):
        """
        Check every minute if there are overdue jobs
        """
        self.notifier = Timer(60.0, self.check_overdue_jobs)
        self.notifier.daemon = True
        self.notifier.start()

    def stop_timeout_notifier(self):
        """
        """
        self.notifier.cancel()

    def help(self, msg, status, desc, chat_id):
        """
        Print help text to chat.
        """

        # Make sure we don't trigger ourselves with the help text
        if not desc:
            msg.Chat.SendMessage(HELP_TEXT)

# Export the instance to Sevabot
sevabot_handler = CourceHandler()

__all__ = ["sevabot_handler"]