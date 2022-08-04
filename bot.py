import asyncio
import logging
import platform

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ParseMode
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aioredis.exceptions import ConnectionError as RedisConnectionError

from app.handlers import register_handlers

logger = logging.getLogger('app')


async def set_commands(bot: Bot):
    """ Register commands for displaying in Telegram interface """
    commands = [
        BotCommand(command='/cancel', description='Return to main menu'),
        BotCommand(command='/cards', description='Search Hearthstone cards'),
        BotCommand(command='/decks', description='Search Hearthstone decks'),
        BotCommand(command='/decode', description='Get deck from deckstring'),
    ]
    await bot.set_my_commands(commands)


async def main():
    logger.info('Starting bot')

    from app.config import config

    bot = Bot(token=config.bot.TOKEN, parse_mode=ParseMode.HTML)

    try:
        storage = RedisStorage2(
            host='redis',
            port=6379,
            db=5,
            password=config.storage.PASSWORD,
            prefix='fsm',
        )
        await storage.get_states_list()     # check Redis availability
        logger.info('Using Redis')
    except RedisConnectionError:
        storage = MemoryStorage()
        logger.info('Using memory storage')

    dp = Dispatcher(bot, storage=storage)

    register_handlers(dp)

    await set_commands(bot)

    await dp.skip_updates()
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()


def cli():
    """ Wrapper for command line """
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped')


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    cli()
