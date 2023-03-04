from aiogram.utils import executor

from create_bot import dp, bot

import handlers
from models import db, CustomUser

handlers.register_handlers_start(dp)
handlers.register_handlers_my_referrals(dp)
handlers.register_handlers_my_profile(dp)
handlers.register_handlers_deal(dp)


async def on_startup(_):
    print('started')

    with db:
        CustomUser.create_table()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
