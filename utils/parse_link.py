
def parse_link(url):

    if url.startswith("www."):
        return url[4:].rstrip("/")
    
    return url.rstrip("/")
