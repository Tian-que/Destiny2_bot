from nonebot.rule import Rule
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State

def check_group_message() -> Rule:
    async def _checker(bot: Bot, event: Event, state: T_State) -> bool:
        if event.get_event_name().startswith('message.group'):
            return True
        return False
    return Rule(_checker)

def check_setu_bans() -> Rule:
    async def _checker(bot: Bot, event: Event, state: T_State) -> bool:
        if event.get_event_name().startswith('message.group'):
            return True
        return False
    return Rule(_checker)