import pytest_asyncio
import time
import asyncio

import discord
import discord.ext.test as dpytest


@pytest_asyncio.fixture(scope="session")
async def bot():
    from pubobot import console, scheduler, bot, stats3, config, client

    console.init(enable_input=False)
    scheduler.init()
    bot.init()
    stats3.init()
    config.init()
    client.init()

    dpytest.configure(client.c, num_members=20)

    async def run_background_tasks():
        while True:
            if not console.alive:
                await client.close()
                break

            frametime = time.time()
            bot.run(frametime)
            scheduler.run(frametime)
            console.run()

            await client.send()
            await asyncio.sleep(0.001)

    loop = asyncio.get_running_loop()
    background_task = loop.create_task(run_background_tasks())

    yield client.c

    console.terminate()
    await background_task


class Helper:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_running_loop()

    async def message(self, peek=False, timeout=0.5) -> discord.Message:
        start = time.time()
        while dpytest.sent_queue.empty() and time.time() - start < timeout:
            await asyncio.sleep(0.001)

        if dpytest.sent_queue.empty():
            raise TimeoutError()

        if peek:
            return dpytest.sent_queue.peek()

        return dpytest.sent_queue.get_nowait()


@pytest_asyncio.fixture(scope="session")
async def helper():
    return Helper(asyncio.get_running_loop())
