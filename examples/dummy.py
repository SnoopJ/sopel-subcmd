from sopel import plugin

from sopel_subcmd import SubcommandDispatcher


dispatcher = SubcommandDispatcher()


@dispatcher.register
def dummy_subcmd1(bot, trigger, *args, **kwargs):
    bot.say(f"dummy:subcmd1 subcommand (args={args!r}, kwargs={kwargs!r})")


@dispatcher.register
def dummy_subcmd2(bot, trigger, *args, **kwargs):
    bot.say(f"dummy:subcmd2 subcommand (args={args!r}, kwargs={kwargs!r})")

@dispatcher.register
def dummy_猫(bot, trigger, *args, **kwargs):
    bot.say("にゃあああー")


# ç = U+0063 U+0327
@dispatcher.register
def dummy_çava(bot, trigger, *args, **kwargs):
    bot.say("ça va")


@dispatcher.register
def dummy_パイソン(bot, trigger, *args, **kwargs):
    bot.say("\N{SNAKE}")


@plugin.commands(
        "dummy",
        "dummy:subcmd1",
        "dummy:subcmd2",
        "dummy:猫",

        # NOTE:we need to repeat our command for Sopel to match different codepoint sequences,
        # but dispatch will find the function whose name is equivalent under NFKC normalization (which Python uses)
        "dummy:çava",        # ç = U+00e7
        "dummy:çava",        # ç = U+0063 U+0327
        "dummy:パイソン",
        "dummy:ﾊﾟｲｿﾝ",
)
def dummy(bot, trigger):
    data = 42
    moredata = "Twas brillig and the slithy toves"

    if dispatcher.dispatch_subcmd(bot, trigger, data, moredata=moredata):
        # we successfully dispatched to a subcommand, the base command has no more work
        return

    bot.say(f"base command, invoked as {trigger.group(0)!r}")
