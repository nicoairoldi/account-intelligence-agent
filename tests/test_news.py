import pytest
from unittest.mock import patch, Mock
from fetchers.news import RetryExhaustedError, _call_api, AuthError, RateLimitError, ServerError, get_news


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

class TestGetNews: 
    @patch("fetchers.news.time.sleep")
    @patch("fetchers.news._call_api")
    def test_returns_article_on_first_try(self, mock_call_api, mock_sleep):
        articles = [{"title": "Evergy Progress Update"}, {"title": "Evergy Infrastructure"}]
        mock_call_api.return_value = articles
        result = get_news("Evergy")
        assert result == articles

    @patch("fetchers.news.time.sleep")
    @patch("fetchers.news._call_api")
    def test_auth_error_propagates_without_retry(self, mock_call_api, mock_sleep):
        mock_call_api.side_effect = AuthError(status_code=401)
        with pytest.raises(AuthError):
            get_news("Evergy")
        
        mock_sleep.assert_not_called()
    

    @patch("fetchers.news.time.sleep")
    @patch("fetchers.news._call_api")
    def test_retry_on_rate_limit_error_and_succeed(self, mock_call_api, mock_sleep):
        articles = [{"title": "Evergy Progress Update"}, {"title": "Evergy Infrastructure"}]
        mock_call_api.side_effect = [RateLimitError(status_code=429), articles]
        result = get_news("Evergy")
        assert result == articles
        assert mock_call_api.call_count == 2
        mock_sleep.assert_called_once_with(3)

    @patch("fetchers.news.time.sleep")
    @patch("fetchers.news._call_api")
    def test_retry_on_server_error_and_succeed(self, mock_call_api, mock_sleep):
        articles = [{"title": "Evergy Progress Update"}, {"title": "Evergy Infrastructure"}]
        mock_call_api.side_effect = [ServerError(status_code=500), articles]
        result = get_news("Evergy")
        assert result == articles
        assert mock_call_api.call_count == 2
        mock_sleep.assert_called_once_with(3)


    @patch("fetchers.news.time.sleep")
    @patch("fetchers.news._call_api")
    def test_retry_exhausted_raises_exception(self, mock_call_api, mock_sleep):
        mock_call_api.side_effect = [RateLimitError(status_code=429)] * 4
        with pytest.raises(RetryExhaustedError):
            get_news("Evergy")
        assert mock_call_api.call_count == 4
        assert mock_sleep.call_count == 3