"""Exception handlers for FastAPI"""

from fastapi import FastAPI


def register_exception_handlers(app: FastAPI) -> None:
    """register_exception_handlers"""

    # TODO: implement exception handlers
    print(f"register_exception_handlers for app: {app.title}")
