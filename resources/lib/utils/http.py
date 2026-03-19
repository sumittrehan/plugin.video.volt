import json
import socket
import time

try:
    # Kodi usually provides urllib
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    Request = None
    urlopen = None
    URLError = Exception
    HTTPError = Exception


class HttpClientError(Exception):
    pass


class HttpClient:
    DEFAULT_HEADERS = {
        'User-Agent': 'Kodi-Volt-Addon/1.0',
        'Content-Type': 'application/json',
    }

    def __init__(self, timeout=15):
        self.timeout = timeout

    def request(self, url, method='GET', headers=None, payload=None):
        headers = headers or {}
        merged = self.DEFAULT_HEADERS.copy()
        merged.update(headers)

        data = None
        if payload is not None:
            if isinstance(payload, (dict, list)):
                data = json.dumps(payload).encode('utf-8')
            elif isinstance(payload, str):
                data = payload.encode('utf-8')
            else:
                data = payload

        request = Request(url, data=data, headers=merged, method=method)

        try:
            response = urlopen(request, timeout=self.timeout)
            raw = response.read().decode('utf-8')
            return json.loads(raw) if raw else {}
        except HTTPError as e:
            try:
                body = e.read().decode('utf-8')
                details = json.loads(body)
            except Exception:
                details = body
            raise HttpClientError(f"HTTP {e.code}: {e.reason} {details}")
        except URLError as e:
            raise HttpClientError(f"URL error: {e}")
        except socket.timeout:
            raise HttpClientError("Request timed out")
        except ValueError:
            raise HttpClientError("Non-JSON response")
        except Exception as e:
            raise HttpClientError(str(e))
