This plugin for the IRC bot [Sopel](https://sopel.chat) allows for 

### Installation

```bash
$ pip install sopel-subcmd
```

### Example usage

Import the `SubcommandDispatcher` class to your plugin, register handlers
for your desired subcommands, and call it with the `bot, trigger` associated
with your event. The return value indicates if a subcommand handler was found
and called. Note that exceptions from handlers are allowed to propagate freely.

```python
from sopel import plugin
from sopel_subcmd import SubcommandDispatcher


dispatcher = SubcommandDispatcher()

@dispatcher.register
def dummy_subcmd1(bot, trigger, *args, **kwargs):
    bot.say(f"dummy:subcmd1 subcommand (args={args!r}, kwargs={kwargs!r})")


@dispatcher.register
def dummy_subcmd2(bot, trigger, *args, **kwargs):
    bot.say(f"dummy:subcmd2 subcommand (args={args!r}, kwargs={kwargs!r})")


@plugin.commands(
        "dummy",
        "dummy:subcmd1",
        "dummy:subcmd2",
        "dummy:fakesub",  # this pattern has no dedicated handler, we will use the base
)
def dummy(bot, trigger):
    # We can do some computations common to every command before dispatch, if appropriate
    data = 42
    moredata = "Twas brillig and the slithy toves"

    # automatically hand off to the subcommand handlers, if appropriate
    if dispatcher.dispatch_subcmd(bot, trigger, data, moredata=moredata):
        return

    # we don't *have* to pass data to the handler if ``bot, trigger`` would be enough
    # if _dispatch_subcmd(bot, trigger):
    #     return

    bot.say(f"base command, invoked as {trigger.group(0)!r}")
```

The above sample plugin produces the following behavior:

```
<SnoopJ> !dummy
<testibot> base command, invoked as '!dummy'
<SnoopJ> !dummy:subcmd1
<testibot> dummy:subcmd1 subcommand (args=(42,), kwargs={'moredata': 'Twas brillig and the slithy toves'})
<SnoopJ> !dummy:subcmd2
<testibot> dummy:subcmd2 subcommand (args=(42,), kwargs={'moredata': 'Twas brillig and the slithy toves'})
<SnoopJ> !dummy:fakesub
<testibot> base command, invoked as '!dummy:fakesub'
<SnoopJ> !version
<testibot> [version] Sopel v8.0.0.dev0 | Python: 3.7.16 | Commit: b5eba03ce74baae36e3456ac938686fb23f5671b
```

### Unicode support

Because Python has excellent support for Unicode identifiers, you can dispatch
to functions whose names are written in nontrivial scripts:

```python
from sopel_subcmd import SubcommandDispatcher


dispatcher = SubcommandDispatcher()

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
        "dummy:猫",

        # NOTE:we need to repeat our command for Sopel to match different codepoint sequences,
        # but dispatch will find the function whose name is equivalent under NFKC normalization (which Python uses)
        "dummy:çava",        # ç = U+00e7
        "dummy:çava",        # ç = U+0063 U+0327
        "dummy:パイソン",
        "dummy:ﾊﾟｲｿﾝ",
)
def dummy(bot, trigger):
    # We can do some computations common to every command before dispatch, if appropriate
    data = 42
    moredata = "Twas brillig and the slithy toves"

    # automatically hand off to the subcommand handlers, if appropriate
    if dispatcher.dispatch_subcmd(bot, trigger, data, moredata=moredata):
        return

    bot.say(f"base command, invoked as {trigger.group(0)!r}")
```

Which makes the feature a little more transparent on the user-facing side

```
<SnoopJ> !dummy:猫
<testibot> にゃあああー
<SnoopJ> !dummy:çava
<testibot> ça va
<SnoopJ> !dummy:çava
<testibot> ça va
<SnoopJ> !dummy:パイソン
<testibot> 🐍
<SnoopJ> !dummy:ﾊﾟｲｿﾝ
<testibot> 🐍
```

### Misc.

If needed, you can check the version of this plugin using Sopel's `version` command:

```
<SnoopJ> !version sopel-subcmd
<testibot> [version] sopel-subcmd v1.0.0
```

#### Known issues

* subcommands whose names are invalid function names are not normalized
