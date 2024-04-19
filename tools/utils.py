import urllib.request

def request(url: str):
    """ Download data from the given url. """
    
    with urllib.request.urlopen(url) as response:
        headers = response.headers
        charset = headers.get_content_charset() or "utf-8"
        stream = response.read()
        return stream.decode(charset)