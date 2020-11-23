import json
import pytest
from unittest.mock import Mock

from .. import *
from .stubs import responses


RESPONSE_DATA = responses.SAMPLES


MOCK_REQUEST = Mock(
    text=None,
    status_code=200,
    closed=False
)


def mocked_request(uri, *args, **kwargs):
    end_point = uri.split('/')[-1]

    response_text = RESPONSE_DATA.get(end_point, "Bad request")

    MOCK_REQUEST.data = response_text

    MOCK_REQUEST.text = json.dumps(response_text) if isinstance(
        response_text, dict) else response_text

    MOCK_REQUEST.end_point = end_point
    MOCK_REQUEST.url = uri
    MOCK_REQUEST.args = json.loads(args[0])
    MOCK_REQUEST.kwargs = kwargs
    return MOCK_REQUEST


@pytest.fixture
def post_request(monkeypatch):
    monkeypatch.setattr('requests.post', mocked_request)


@pytest.fixture
def mock_request(post_request):
    MOCK_REQUEST.reset_mock()
    yield MOCK_REQUEST
    MOCK_REQUEST.reset_mock()


@pytest.fixture
def mock_api(mock_request):
    yield Api
    Api.API_KEY = None
