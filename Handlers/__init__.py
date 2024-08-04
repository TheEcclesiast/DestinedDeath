from aiogram import Router


from .commands import command_router


handlers_router = Router()

handlers_router.include_router(command_router)
