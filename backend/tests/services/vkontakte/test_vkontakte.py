import asyncio

import pytest
from fastapi import HTTPException

from backend.services.vkontakte.vk_api import VKError


NON_CRITICAL_ERRORS_CASES = [
    {
        "error_code": 6,
        "error_msg": "Too many requests",
    },
    {
        "error_code": 6,
        "error_msg": "Too many requests!",
    },
]

CRITICAL_ERRORS_CASES = [
    {
        "error_code": 100,
        "error_msg": "owner_id is undefined",
    },
    {
        "error_code": 34,
        "error_msg": "Something bad",
    },
    {
        "error_code": 51,
        "error_msg": "Something very bad",
    },
]


@pytest.mark.parametrize("non_critical_error", NON_CRITICAL_ERRORS_CASES)
def test_vk_error_non_critical(non_critical_error):
    error = VKError(non_critical_error, {})

    error.handle_error_sync()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(error.handle_error_async())

    assert True


@pytest.mark.parametrize("critical_error", CRITICAL_ERRORS_CASES)
def test_vk_error_critical(critical_error):
    error = VKError(critical_error)

    try:
        error.handle_error_sync()
        assert False
    except HTTPException:
        assert True

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(error.handle_error_async())
        assert False
    except HTTPException:
        assert True
    except Exception:
        assert False


def test_vk_error_critical_100():
    domain = "test_domain"
    error = VKError(
        error={
            "error_code": 100,
            "error_msg": "owner_id is undefined",
        },
        params={"domain": domain},
    )

    try:
        error.handle_error_sync()
        assert False
    except HTTPException:
        assert True

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(error.handle_error_async())
        assert False
    except HTTPException as exc:
        assert exc.detail == f"Человек/сообщество с адресом {domain} не найдены."
    except Exception:
        assert False
