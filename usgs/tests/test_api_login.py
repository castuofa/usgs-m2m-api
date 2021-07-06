import pytest


def test_login_with_instance_login_and_pass(mock_request, mock_api):
    mock_api("test", "pass")
    assert mock_api.API_KEY == mock_request.data.get("data")


def test_login_with_manual_login_and_pass(mock_request, mock_api):
    mock_api.login("test", "pass")
    assert mock_api.API_KEY == mock_request.data.get("data")


def test_login_with_env_vars(mock_request, mock_api, monkeypatch):
    monkeypatch.setenv("EE_USER", "login")
    monkeypatch.setenv("EE_PASS", "password")

    mock_api.login()

    assert mock_api.API_KEY == mock_request.data.get("data")
    assert mock_request.args.get("username") == "login"
    assert mock_request.args.get("password") == "password"


def test_login_creds_will_force_user_prompt(mock_request, mock_api, monkeypatch):
    monkeypatch.delenv("EE_USER", raising=False)
    monkeypatch.delenv("EE_PASS", raising=False)
    monkeypatch.setattr("builtins.input", lambda _: "test_user")
    monkeypatch.setattr("getpass.getpass", lambda _: "test_pass")

    mock_api.login()

    assert mock_api.API_KEY is not None
    assert mock_request.args.get("username") == "test_user"
    assert mock_request.args.get("password") == "test_pass"


def test_login_creds_cannot_by_empty(mock_api, monkeypatch):
    monkeypatch.delenv("EE_USER", raising=False)
    monkeypatch.delenv("EE_PASS", raising=False)
    monkeypatch.setattr("builtins.input", lambda _: None)
    monkeypatch.setattr("getpass.getpass", lambda _: None)

    with pytest.raises(ValueError):
        mock_api.login()

    assert mock_api.API_KEY is None
