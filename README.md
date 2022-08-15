# HS Deck Helper Bot

Asynchronous Telegram bot-wrapper for [HS Deck Helper](https://github.com/ysaron/hearthstone-deck-helper) API.  

> [@hdhapiwrapper_bot](https://t.me/hdhapiwrapper_bot)

The bot allows you to construct requests to the HS Deck Helper API using Telegram buttons and receive formatted responses.  

### Stack

- Python 3.10
- aiogram
- aiohttp
- Redis
- pytest & asynctest
- Docker & docker-compose

### Features

Supported HS Deck Helper API features:  
- **[Card search](#card-search-example)** by
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

### Interaction scheme

![interaction](/pics/Interaction.png)


### Card search example

![card_search_start](/pics/card_search_01.png)

Click the **Type** Button:

![card_search_types_1](/pics/card_search_02.png)

Select **Location** - a new type of Hearthstone cards. The **Health** parameter is now available:

![card_search_types_location](/pics/card_search_03.png)

Change **Type**:

![card_search_types_2](/pics/card_search_04.png)

Select **Minion**. Another parameters are now available:

![card_search_types_minion](/pics/card_search_05.png)

Let's set a couple more parameters:

![card_search_more_params](/pics/card_search_06.png)

Press **REQUEST** button. A request to HS Deck Helper API will be executed.  

![card_search_response_list](/pics/card_search_07.png)

Links lead to card renders.  
Select a specific card. A request to HS Deck Helper API will be executed.    

![card_search_response_detail](/pics/card_search_08.png)

Similarly, the search for decks is performed.  
