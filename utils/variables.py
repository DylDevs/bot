from types import SimpleNamespace
from utils.classes import Asset
from discord import Intents
import os

# Extract environment variables
_env_data = open(".env", "r").readlines()
_env_data = [x.strip() for x in _env_data]

_env_dictionary = {}
for i in _env_data:
    key = i.split("=")[0]
    value = i.replace(i.split("=")[0] + "=", "")
    if "," in value: # Support lists
        value = [x.strip() for x in value.split(",")]
        for i, val in enumerate(value):
            try: # Try to convert to int
                value[i] = int(val)
            except ValueError:
                pass

    try: # Try to convert to int
        if type(value) == str:
            value = int(value)
    except ValueError:
        pass
    
    _env_dictionary[key] = value

ENV = SimpleNamespace(**_env_dictionary)
"""Enviroment variables"""
ENV.ADMINS = [ENV.ADMINS] if isinstance(ENV.ADMINS, int) else ENV.ADMINS
"""Explicitly ensure that ENV.ADMINS is a list"""

# General constants and URLs
PREFIX: str = "!"
"""The prefix for commands"""
UMAMI_API = "https://umami.ets2la.com/api"
"""Unami stats API endpoint"""
SUPPORT_API_BASE = "localhost:8001"
"""Base URL for the ETS2LA chat support API"""
SUPPORT_WS = f"ws://{SUPPORT_API_BASE}/ws/bot"
"""ETS2LA chat support websocket endpoint for relaying messages"""
SUPPORT_API = f"http://{SUPPORT_API_BASE}/"
"""ETS2LA chat support API endpoint for sending metadata"""
DISCORD_WEBHOOK = f"https://discord.com/api/webhooks/1384921134008369222/eU_4XGooncwJNGxiDZ5A0fDF361qQodbf9AxIwXXDoKRr69wgb5B9tw6rSkIMbZd1qiP"
"""Webhook which allows for bot users to send messages to the support channel"""

# Channels (Commented out channels are for the main ETS2LA server)
#TRANSLATION_UPDATE_CHANNEL = 1381627489574453258
TRANSLATION_UPDATE_CHANNEL = 1272294263874654240
"""The channel to send translation updates to (Text)"""
#UPDATE_CHANNEL = 1381627373627244655
UPDATE_CHANNEL = 1120734880133820537
"""The channel to send updates to (Text)"""
#
SUPPORT_TICKET_CHANNEL = 1381289250733166592
"""The channel to send support tickets to (Forum)"""

# Paths
PATH = os.path.dirname(os.path.dirname(__file__))
"""Root of the filesystem"""
LOG_FILE = os.path.join(PATH, "bot.log")
"""The path to the log file"""
ASSETS_FOLDER = os.path.join(PATH, "Assets")
"""The path where assets are stored"""
VERIFIED_USERS_FILE = os.path.join(PATH, "Assets", "verified.txt")
"""The path to the list of verified users"""
ASSET_URLS : list[Asset] = [
    Asset(
        "ETS2LA", 
        "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist", 
        ASSETS_FOLDER,
        "--depth=20 --single-branch"
    ),
    Asset(
        "Translations", 
        "https://github.com/ETS2LA/translations", 
        ASSETS_FOLDER
    )
]
"""Defintion of assets and their URLs"""

# Discord config
INTENTS = Intents.default()
INTENTS.message_content = True
INTENTS.presences = True
INTENTS.members = True
"""Intent config for discord bot"""