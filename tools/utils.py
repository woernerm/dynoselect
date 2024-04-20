import urllib.request
import gzip
import tarfile
import zipfile
import io
from contextlib import closing
from pathlib import PurePath

def request(url: str):
    """Request data from the given url or local file and decompress gzip formats. 

    Args:
        url: The url or file path to read from.
    """
    with closing(urllib.request.urlopen(url)) as response:
        headers = response.headers
        charset = headers.get_content_charset() or "utf-8"
        contenttype = headers.get_content_type()
        
        if contenttype == "application/x-tar":
            mode = PurePath(url).suffix[1:]  # Remove leading dot from suffix.
            # Read the response into a file-like object so that the tarfile module can
            # seek in both directions within the file.
            file = io.BytesIO(response.raw.read())
            return tarfile.open(fileobj=file, mode=f"r:{mode}")
        
        if contenttype == "application/zip":
            file = io.BytesIO(response.read())
            return zipfile.ZipFile(file)

        stream = response.read()
        if contenttype == "application/gzip":
            return gzip.decompress(stream).decode(charset)
        return stream.decode(charset)
