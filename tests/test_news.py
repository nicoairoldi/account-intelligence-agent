import pytest
from unittest.mock import patch, Mock
from fetchers.news import _call_api, AuthError, RateLimitError, ServerError


class TestCallApi:
    @patch("fetchers.news.requests.get")
    def test_401_raises_auth_error(self, mock_get):
        mock_response = Mock(status_code=401)
        mock_get.return_value = mock_response
        with pytest.raises(AuthError) as exc_info:
            _call_api("Evergy")
        assert exc_info.value.status_code == 401

    @patch("fetchers.news.requests.get")
    def test_429_raises_rate_limit_error(self, mock_get):
        mock_response = Mock(status_code=429)
        mock_get.return_value = mock_response
        with pytest.raises(RateLimitError) as exc_info:
            _call_api("Evergy")
        assert exc_info.value.status_code == 429

    @patch("fetchers.news.requests.get")
    def test_500_raises_server_error(self, mock_get):
        mock_response = Mock(status_code=500)
        mock_get.return_value = mock_response
        with pytest.raises(ServerError) as exc_info:
            _call_api("Evergy")
        assert exc_info.value.status_code == 500

    @patch("fetchers.news.requests.get")
    def test_200_returns_articles(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"articles": [{"title": "Evergy news"}]}
        mock_get.return_value = mock_response
        result = _call_api("Evergy")
        assert result == [{"title": "Evergy news"}]