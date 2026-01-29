"""Entry point for barry-server command."""
import asyncio
from barry_server.server import main


def run():
    """Synchronous entry point that runs the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
