# HS Deck Helper Bot

Asynchronous Telegram bot-wrapper for [HS Deck Helper](https://github.com/ysaron/hearthstone-deck-helper) API.  

> [@hdhapiwrapper_bot](https://t.me/hdhapiwrapper_bot)

The bot allows you to construct requests to the HS Deck Helper API using Telegram buttons and receive formatted responses.  

### Stack

- Python3.10
- aiogram
- aiohttp
- Redis
- pytest & asynctest
- Docker & docker-compose

### Features

Supported HS Deck Helper API features:  
- **Card search** by
  - *name*
  - *type* (Minion, Spell, Location etc)
  - *class* (Priest, Warlock, Druid, Neutral etc)
  - *set* (Core, Castle Nathria etc)
  - *rarity* (Legendary, Epic etc)
  - *numeric parameters* (cost, attack, health etc; depending on type)
- **Deck search** by
  - *format* (Standard, Wild, Classic)
  - *class* (Priest, Warlock, Druid etc)
  - *date of creation*
  - *included cards* (search for cards inside the deck search)
- **Decoding decks** from
  - pure deck code
  - full decklist (that is copied from the game client)
