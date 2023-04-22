from typing import Any, Optional, TypedDict

from yarl import URL


class RequestDict(TypedDict):
    """
    A TypedDict representing the request dictionary for an aiohttp ClientSession request.

    Attributes:
        url (str): The URL of the request.
        params (dict): The GET parameters.
        data (Optional[Any]): The data parameters for POST requests.
        method (str): The request method.
        body (Optional[str]): The raw body, if present.
    """

    url: str
    params: dict
    data: Optional[Any]
    method: str


class URLTemplateBuilder:
    """
    A class that provides a URL template builder for API endpoints.

    Attributes:
        template (str): The URL template with placeholders.
    """

    def __init__(self, template: str):
        self.template = template

    def url(self, **kwargs) -> "URLBuilder":
        """
        Initiates the URL builder and fills the template with the given keyword arguments.

        Args:
            **kwargs: The keyword arguments to fill the template.

        Returns:
            URLBuilder: The URLBuilder instance.
        """
        url = self.template.format(**kwargs)
        return URLBuilder(url)


class URLBuilder:
    """
    A class that builds the URL with additional parameters.

    Attributes:
        _url (str): The base URL.
        _params (dict): The GET parameters.
        _data (Any): The data parameters for POST requests.
        _method (str): The request method.
    """

    def __init__(self, url: str):
        self._url = url
        self._params = {}
        self._data = None
        self._method = "GET"

    def query(self, **kwargs) -> "URLBuilder":
        """
        Sets the query parameters for the URL.

        Args:
            **kwargs: The keyword arguments for the query parameters.

        Returns:
            URLBuilder: The URLBuilder instance.
        """
        self._params.update(kwargs)
        return self

    def data(self, data: Any) -> "URLBuilder":
        """
        Sets the data parameters for POST requests.

        Args:
            data (Any): The data.

        Returns:
            URLBuilder: The URLBuilder instance.
        """
        self.data.update(data)
        return self

    def method(self, method: str) -> "URLBuilder":
        """
        Sets the request method.

        Args:
            method (str): The request method, e.g., 'GET', 'POST', etc.

        Returns:
            URLBuilder: The URLBuilder instance.
        """
        self._method = method
        return self

    def build(self) -> RequestDict:
        """
        Builds the request dictionary that can be expanded into an aiohttp ClientSession request.

        Returns:
            RequestDict: The request dictionary.
        """
        request: RequestDict = {
            "url": self._url,
            "params": self._params,
            "data": self._data,
            "method": self._method,
        }
        return request

    def build_url(self) -> URL:
        """
        Builds the URL with the given data (including GET parameters).

        Returns:
            URL: The built URL as a yarl.URL.
        """
        url = URL(self._url)
        url = url.with_query({**url.query, **self._params})
        return url
