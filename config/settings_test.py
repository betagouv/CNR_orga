from dotenv import load_dotenv


load_dotenv(".env.test")

from config.settings import *  # noqa: F401, E402, F403
