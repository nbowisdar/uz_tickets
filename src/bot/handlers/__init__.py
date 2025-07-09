import importlib
import os
import pkgutil

from aiogram import Router


def get_handlers_router() -> Router:
    router = Router()
    package_dir = os.path.dirname(__file__)

    # Iterate through all modules in the current package
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        # Skip __init__.py and other non-router modules if needed
        if module_name.startswith("__"):
            continue

        # Dynamically import the module
        module = importlib.import_module(f".{module_name}", package=__name__)

        # Check if the module has a 'router' attribute
        if hasattr(module, "router") and isinstance(module.router, Router):
            router.include_router(module.router)


    return router
