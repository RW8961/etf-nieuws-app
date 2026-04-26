class NewsAPIError(Exception):
    pass


class NewsAPIRateLimitError(NewsAPIError):
    pass
