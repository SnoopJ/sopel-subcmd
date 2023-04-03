from collections import ChainMap
import inspect
import logging
from typing import Tuple

__all__ = [
    "parse_subcmd",
    "dispatch_subcmd",
]

LOGGER = logging.getLogger(__name__)


def parse_subcmd(bot, trigger, subcmd_sep: str) -> Tuple[str, str]:
    """Parse a trigger into a ``(cmd, subcmd)`` pair.

    :param bot: the ``Sopel`` instance associated with this event.
    :param trigger: the ``Trigger`` instance associated with this event.
    :param subcmd_sep: the separator between command and subcommand.

    NOTE: ``subcmd`` can be empty if a subcommand is not present.
    """
    cmd, sep, subcmd = trigger.group(0).partition(subcmd_sep)
    N_prefix = len(bot.settings.core.prefix)
    prefix, cmd = cmd[:N_prefix-1], cmd[N_prefix-1:]

    return cmd, subcmd


def dispatch_subcmd(bot, trigger, *func_args, subcmd_sep: str = ":", **func_kwargs) -> bool:
    """Dispatch the given trigger to a subcommand, if one is defined in the calling context.

    :param bot: the ``Sopel`` instance associated with this event.
    :param trigger: the ``Trigger`` instance associated with this event.
    :param subcmd_sep: the separator between command and subcommand.

    Returns ``False`` if a subcommand handler could not be located, ``True``
    otherwise.

    Note: ``func_args, func_kwargs`` will be passed to the handler as-is.
    Note: this helper passes all exceptions from the handler to the caller.
    """
    cmd, subcmd = parse_subcmd(bot, trigger, subcmd_sep=subcmd_sep)

    # NOTE: we check in the calling frame for the target name
    frames = inspect.getouterframes(inspect.currentframe())
    caller_frame = frames[1].frame
    try:
        func_name = f"{cmd}_{subcmd}"
        func = ChainMap(caller_frame.f_locals, caller_frame.f_globals)[func_name]
    except LookupError:
        LOGGER.debug("Cannot find subcommand handler %r", func_name)
        return False

    func(bot, trigger, *func_args, **func_kwargs)
    return True
