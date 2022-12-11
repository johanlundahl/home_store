from dataclasses import dataclass
from home_store.config import Configuration


@dataclass
class Server:
    address: str = 'localhost'
    port: int = 5000


@dataclass
class Config(Configuration):
    server: Server = Server()


if __name__ == '__main__':
    config = Config.init()
