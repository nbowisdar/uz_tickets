from bot.config import get_config


config = get_config()

if __name__ == "__main__":
    if config.USE_WEBHOOK:
        import uvicorn
        from api.main import app

        uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
    else:
        import asyncio
        from bot.main import start_pooling

        asyncio.run(start_pooling())
