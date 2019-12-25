import requests
import xml.etree.ElementTree as ET

from secret import GOODREADS_KEY
from secret import GOODREADS_USERID


def get_stats():

    resp = requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&shelf=currently-reading&id={GOODREADS_USERID}")
    root = ET.fromstring(resp.content)
    title = root.findall("./reviews/review/book/title")[0].text
    image_url = root.findall("./reviews/review/book/image_url")[0].text
    
    return {'currently_reading': dict(
            stat_id="currently_reading", 
            description="Reading", 
            value=title, 
            image_url=image_url)}
