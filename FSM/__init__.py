from .fsmgroup import cancel_fsm_router, FoeTracer


from aiogram import Router

all_fsm_routers = Router()
all_fsm_routers.include_router(cancel_fsm_router)
all_fsm_routers.include_router(FoeTracer)

__all__ = ["all_fsm_routers"]