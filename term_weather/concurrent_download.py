import threading
from queue import Queue
import urllib.request
from urllib.error import HTTPError

url_list = {"forecast": "https://www.yr.no/sted/Norge/Oslo/Oslo/Oslo/forecast.xml",
            "now": "https://www.yr.no/sted/Norge/Oslo/Oslo/Oslo/varsel_nu.xml"}


def concurrent_download(url_dict):
    """
    Downloads the urls from the input dictionary
    :param url_dict: key: url
    :return: key: content, key is the same key as the input, content is downloaded utf-8 decoded string
    """
    content_dict = {}
    url_queue = Queue()

    def process_queue():
        while True:
            key, current_url = url_queue.get()
            try:
                content = urllib.request.urlopen(current_url).read().decode('utf-8')
            except HTTPError as e:
                # An error during processing failed, we set the content to None
                # FIXME: Is this a good way to handle this situation??? Now we have to verify we have content after join
                content_dict[key] = None
                url_queue.task_done()
                break

            content_dict[key] = content
            url_queue.task_done()

    for i in range(len(url_dict)):
        t = threading.Thread(target=process_queue)
        t.daemon = True
        t.start()
    for key, url in url_dict.items():
        url_queue.put((key, url))
    url_queue.join()

    # Have to verify that we have some content, else raise AssertionError
    for key, content in content_dict.items():
        assert content

    return content_dict

