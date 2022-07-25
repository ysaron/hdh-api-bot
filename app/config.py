import os
from dataclasses import dataclass
import logging
import sys

from pathlib import Path
import ujson

from .exceptions import ArgumentError, ConfigurationError

DEBUG = True        # False if running by Docker
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'app' / 'data'

MAX_CARD_NAME_LENGTH = 30
MAX_CARDS_IN_RESPONSE = 90

logger = logging.getLogger('app')
logging.basicConfig(
    level=logging.INFO,
    format='{asctime} | {levelname:^8s} | {name:^34s} : : : {message}',
    style='{',
)


@dataclass(frozen=True)
class TgBot:
    TOKEN: str
    ADMIN_ID: int


@dataclass(frozen=True)
class RedisConf:
    PASSWORD: str
    MSG_IDS: list[str]


@dataclass(frozen=True)
class HsDeckHelperAPI:
    DOMAIN: str


@dataclass(frozen=True)
class Config:
    bot: TgBot
    storage: RedisConf
    api: HsDeckHelperAPI


@dataclass(frozen=True)
class HSType:
    en: str
    ru: str
    sign: str
    emoji: str


@dataclass(frozen=True)
class HSClass:
    en: str
    ru: str


@dataclass(frozen=True)
class HSRarity:
    en: str
    ru: str
    sign: str
    emoji: str


@dataclass(frozen=True)
class HSSet:
    en: str
    ru: str


@dataclass(frozen=True)
class HSEntities:
    types: list[HSType]
    classes: list[HSClass]
    rarities: list[HSRarity]
    sets: list[HSSet]
    card_params: list[str]
    card_digit_params: list[str]

    def gettype(self, sign: str = None, name: str = None) -> HSType:
        """
        Search card type object by english ``name`` **or** ``sign``.

        :param sign: a short, language-independent designation
        :param name: english type name
        :return: HSType object
        :raise StopIteration: if type not found
        :raise ArgumentError: if both or none of (sign, name) params are provided
        """

        if sign and name:
            raise ArgumentError('Only one of the parameters (sign, name) must be provided')
        if sign:
            return next(t for t in self.types if t.sign == sign)
        if name:
            return next(t for t in self.types if t.en == name)
        raise ArgumentError('One of the parameters (sign, name) must be provided')

    def getrarity(self, sign: str = None, name: str = None) -> HSRarity:
        """
        Search card rarity object by english ``name`` **or** ``sign``.

        :param sign: a short, language-independent designation
        :param name: english rarity name
        :return: HSRarity object
        :raise StopIteration: if rarity not found
        :raise ArgumentError: if both or none of (sign, name) params are provided
        """

        if sign and name:
            raise ArgumentError('Only one of the parameters (sign, name) must be provided')
        if sign:
            return next(r for r in self.rarities if r.sign == sign)
        if name:
            return next(r for r in self.rarities if r.en == name)
        raise ArgumentError('One of the parameters (sign, name) must be provided')


def load_config() -> Config:
    """ Load and return bot configuration data """
    token = os.environ.get('TOKEN')
    admin_id = os.environ.get('ADMIN_ID')
    api_domain = os.environ.get('HDH_API_DOMAIN')
    redis_password = os.environ.get('REDIS_HOST_PASSWORD')
    if not all([token, admin_id, api_domain]):
        raise ConfigurationError("Couldn't load environment variables")

    return Config(
        bot=TgBot(
            TOKEN=token,
            ADMIN_ID=int(admin_id),
        ),
        storage=RedisConf(
            PASSWORD=redis_password,
            MSG_IDS=[
                'card_request_msg_id',
                'card_prompt_msg_id',
                'card_response_msg_id',
            ]
        ),
        api=HsDeckHelperAPI(
            DOMAIN=api_domain,
        )
    )


def load_hearthstone_data() -> HSEntities:
    """ Load and return Hearthstone-specific static data """
    with open(DATA_DIR / 'hs_entities.json', encoding='utf-8') as f:
        ent = ujson.load(f)
        classes = [HSClass(en=cls['enUS'], ru=cls['ruRU']) for cls in ent['classes'].values()]
        types = [HSType(en=t['enUS'], ru=t['ruRU'], sign=t['sign'], emoji=t['emoji'])
                 for t in ent['types'].values()]
        rars = [HSRarity(en=r['enUS'], ru=r['ruRU'], sign=r['sign'], emoji=r['emoji'])
                for r in ent['rarities'].values()]
        sets = [HSSet(en=s['enUS'], ru=s['ruRU']) for s in ent['sets'].values()]
        card_digit_params = ['cost', 'attack', 'health', 'durability', 'armor']
        card_params = ['name', 'ctype', 'classes', 'cset', 'rarity'] + card_digit_params
        return HSEntities(types=types, classes=classes, rarities=rars, sets=sets,
                          card_params=card_params, card_digit_params=card_digit_params)


try:
    logger.info('Load configuration...')
    config = load_config()
    hs_data = load_hearthstone_data()

    BASE_URL = f'http://{config.api.DOMAIN}/api/v1/'
    CARD_RENDER_BASE_URL = f'http://{config.api.DOMAIN}/media/cards/'
except Exception as e:
    logger.error(f'Configuration error: {e}')
    sys.exit()
else:
    logger.info('Successfully configured')
