import requests
import xml.etree.ElementTree as ET


def get_stats():

    resp = requests.get("https://www.goodreads.com/review/list?key=bW4fWiOzLkUPUK7H92VbCg&v=2&shelf=currently-reading&id=2459559")
    root = ET.fromstring(resp.content)
    title = root.findall("./reviews/review/book/title")[0].text
    image_url = root.findall("./reviews/review/book/image_url")[0].text
    
    return {'currently_reading': dict(
            stat_id="currently_reading", 
            description="Book I'm reading", 
            value=title, 
            image_url=image_url)}
