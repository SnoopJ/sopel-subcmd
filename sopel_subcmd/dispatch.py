import logging
from typing import Callable, Optional, Tuple
import unicodedata

from sopel.bot import Sopel
from sopel.Trigger import Trigger


__all__ = [
    "SubcommandDispatcher",
]

LOGGER = logging.getLogger(__name__)


class SubcommandDispatcher:
    def __init__(self):
        self._handlers = {}

    def register(self, func: Callable):
        name = func.__name__

        name_normed = unicodedata.normalize("NFKC", name)
        self._handlers[name_normed] = func

    def parse_subcmd(self, bot: Sopel, trigger: Trigger, subcmd_sep: str) -> Tuple[str, str]:
        """Parse a trigger into a ``(cmd, subcmd)`` pair.

        :param bot: the ``Sopel`` instance associated with this event.
        :param trigger: the ``Trigger`` instance associated with this event.
        :param subcmd_sep: the separator between command and subcommand.

        NOTE: ``subcmd`` can be empty if a subcommand is not present.
        """
        cmd, sep, subcmd = trigger.group(1).partition(subcmd_sep)

        return cmd, subcmd


    def dispatch_subcmd(self, bot: Sopel, trigger: Trigger, *func_args, subcmd_sep: str = ":", **func_kwargs) -> bool:
        """Dispatch the given trigger to a subcommand, if one is defined in the calling context.

        :param bot: the ``Sopel`` instance associated with this event.
        :param trigger: the ``Trigger`` instance associated with this event.
        :param subcmd_sep: the separator between command and subcommand.

        Returns ``False`` if a subcommand handler could not be located, ``True``
        otherwise.

        Note: ``func_args, func_kwargs`` will be passed to the handler as-is.
        Note: this helper passes all exceptions from the handler to the caller.
        """
        cmd, subcmd = self.parse_subcmd(bot, trigger, subcmd_sep=subcmd_sep)

        # normalize the target identifier in accordance with Python's behavior
        #
        # "All identifiers are converted into the normal form NFKC while
        # parsing; comparison of identifiers is based on NFKC." -- https://docs.python.org/3/reference/lexical_analysis.html#identifiers
        func_name = f"{cmd}_{subcmd}"
        func_name_normed = unicodedata.normalize("NFKC", func_name)
        try:
            func = self._handlers[func_name_normed]
        except LookupError:
            LOGGER.debug("Cannot find subcommand handler %r", func_name)
            return False

        func(bot, trigger, *func_args, **func_kwargs)
        return True
