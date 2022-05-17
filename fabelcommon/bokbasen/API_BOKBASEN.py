import json
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import pytz
import xmltodict
from urllib.parse import urlparse
from rest_framework import status
import time
from fabelcommon.datetime.time_formats import TimeFormats


DOWNLOAD_URL_BASE = 'https://api.dds.boknett.no/content/'


def create_download_url(url_with_id):
    book_id = urlparse(url_with_id).path.strip().rstrip('/').split('/')[-1]
    url = f'{DOWNLOAD_URL_BASE}{book_id}'
    return url


def get_date_time():
    time_gmt = datetime.utcnow()
    date_str = time_gmt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    mytime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    mytime = mytime.replace(tzinfo=pytz.timezone('GMT'))
    return mytime.strftime("%a, %d %b %Y %H:%M:%S %Z")


class Auth():
    def __init__(self, username, password):
        self.url = "https://login.boknett.no/v1/tickets"
        self.username = username
        self.password = password

    def get_ticket(self):
        params = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(self.url, params)

        if response.status_code == 201:
            response = response.headers
            tgt = {
                "boknett-TGT": response.get('Boknett-TGT')
            }
            return tgt
        else:
            return {"Error getting ticket": response.status_code}

    def get_ticket_streaming(self):
        params = {
            "username": "dds_test_abb_fabel",
            "password": "pL2RySNTZWCPudu4"
        }

        response = requests.post("https://login.boknett.webbe.no/v1/tickets/", params)
        print(response)
        if response.status_code == 201:
            response = response.headers
            tgt = {
                "boknett-TGT": response.get('Boknett-TGT')
            }
            return tgt
        else:
            return {'Error getting ticket': response.text}


class Inventory():
    def __init__(self):
        self.url = "https://api.dds.boknett.no/v2/inventory/"

    def parse_inventory_xml(self, response):
        xml_res = xmltodict.parse(response, dict_constructor=dict)
        if 'entry' not in xml_res['feed']:
            return {"Error": "book could not be found"}

        entry = xml_res['feed']['entry']
        if not isinstance(entry, list):
            entry = [entry]

        for entries in entry:
            if entries['inv:access'] == "true" and entries['inv:published'] == "true":
                return entries['id'].replace('urn:uuid:', '')

        return {"Error": "book is not available"}

    def parse_check(self, response):
        xml_res = xmltodict.parse(response, dict_constructor=dict)
        if 'entry' not in xml_res['feed']:
            return False
        entry = xml_res['feed']['entry']
        if isinstance(entry, list):
            for entries in entry:
                if entries['inv:access'] == 'true' and entries['inv:published'] == 'true':
                    return True
            else:
                return False
        if entry['inv:access'] == 'true' and entry['inv:published'] == 'true':
            return True
        else:
            return False

    def get_book_resid(self, tgt, isbn):
        self.url = self.url + isbn + "/"

        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time(),
            "Accept": "application/json"
        }
        params = {
            "after": "",
            "pagesize": ""
        }

        response = requests.get(self.url, headers=head, params=params)
        if response.status_code == 200:

            return self.parse_inventory_xml(response.text)

        else:
            return False

    def check_if_for_sale(self, tgt, isbn):
        self.url = self.url + isbn + "/"

        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time(),
            "Accept": "application/json"
        }
        params = {
            "after": "",
            "pagesize": ""
        }

        response = requests.get(self.url, headers=head, params=params)
        if response.status_code == 200:

            return self.parse_check(response.text)

        else:
            return response.status_code, response.text

    def check_if_for_streaming(self, tgt, isbn):
        url = "https://api.dds.boknett.webbe.no/v2/inventory/" + isbn + '/'

        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time(),
            "Accept": "application/json"
        }
        params = {
            "after": "",
            "pagesize": ""
        }

        response = requests.get(url, headers=head, params=params)
        if response.status_code == 200:

            return self.parse_check(response.text)

        else:
            return response.status_code, response.text


class Order():
    def __init__(self):
        self.url = "https://api.dds.boknett.no/order/"
        self.head = {
            "Authorization": "",
            "Date": get_date_time(),
            "Accept": "application/json",
        }

    def send_order(self, order, tgt):
        self.head["Authorization"] = "Boknett {}".format(tgt['boknett-TGT'])
        self.head['Content-type'] = "application/json"
        payload = json.dumps(order)
        response = requests.post(self.url, headers=self.head, data=payload)
        if response.status_code == 201:
            return response.headers
        else:
            return {"Error": "Could not perform order", "message": response.text, "status": response.status_code}


class Bokskya():
    def __init__(self):
        self.url = "https://idp.dds.boknett.no/"

        self.head = {
            "Authorization": "",
            "Date": get_date_time(),
            "Accept": "application/json",
        }

    def create_user(self, user, tgt):
        self.url = self.url + "register/"
        self.head["Authorization"] = "Boknett {}".format(tgt['boknett-TGT'])
        self.head['Content-type'] = "application/json"

        payload = json.dumps(user)

        response = requests.post(self.url, headers=self.head, data=payload, verify=False)
        if response.status_code == 200:
            return response.text
        else:
            return {"Error": response.text, "Error-code": response.status_code}

    def get_user_by_email(self, email, tgt):
        self.url = self.url + "validate/" + email
        self.head["Authorization"] = "Boknett {}".format(tgt['boknett-TGT'])
        response = requests.get(self.url, headers=self.head)

        # need to introduce global error handling
        if status.is_server_error(response.status_code):
            raise Exception('Error validating user', response.text)

        return json.loads(response.text or 'null')


class Bookshelf():
    def __init__(self):
        self.url = "https://api.dds.boknett.no/catalog/personal/"
        self.head = {
            "Authorization": "",
            "Date": get_date_time()
        }

    def parse_bookshelf_xml(self, response):
        root = ET.fromstring(response.content)

        tags = []
        texts = []
        attribs = []

        bookshelf_list = []

        for child in root.iter('*'):
            tags.append(child.tag)
            texts.append(child.text)
            attribs.append(child.attrib)

        for i in range(len(tags)):
            if tags[i] == '{http://www.w3.org/2005/Atom}entry':

                try:
                    book_obj = {
                        "title": texts[i + 1],
                        "author": texts[i + 11],
                        "image": attribs[i + 2]['href'],
                        "download": attribs[i + 3]['href'],
                        "isbn": texts[i + 16].replace('urn:isbn:', ''),
                    }
                    bookshelf_list.append(book_obj)
                except IndexError:
                    pass

        return bookshelf_list

    def get_bookshelf(self, id_, tgt):

        self.url = self.url + id_
        self.head["Authorization"] = "Boknett {}".format(tgt['boknett-TGT'])

        response = requests.get(self.url, headers=self.head)
        if response.status_code == 200:
            return self.parse_bookshelf_xml(response)
        else:
            return response.text, response.headers, self.url, self.head

    def get_download_url(self, fulfillment_link, tgt):
        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time(),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        params = {
            "type": "audio/vnd.bokbasen.complete-public",
            "bitrate": "64"
        }

        url = create_download_url(fulfillment_link)

        request_download_link = requests.get(url, headers=head, params=params, allow_redirects=False)
        download_status_location = request_download_link.headers['Location']

        while True:
            download_status = requests.get(download_status_location).text
            download_status = xmltodict.parse(download_status, dict_constructor=dict)

            if download_status['downloadStatus']['status'] == "READY":
                return download_status['downloadStatus']['downloadURL']

            time.sleep(0.5)


class Export():
    def __init__(self):
        self.url = "https://api.boknett.no/metadata/export/onix"

    def book_by_isbn(self, tgt, isbn):
        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time()
        }
        self.url = self.url + '/' + isbn
        response = requests.get(url=self.url, headers=head)

        obj = xmltodict.parse(response.content)
        return obj

    def books_after_timestamp(self, tgt, timestamp):
        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time()
        }
        self.url = self.url + '?after=' + timestamp + '&subscription=basic'
        response = requests.get(url=self.url, headers=head)
        obj = xmltodict.parse(response.content)

        return {"onix": obj, "cursor": response.headers['next']}

    def books_after_cursor(self, tgt, cursor):
        head = {
            "Authorization": "Boknett {}".format(tgt['boknett-TGT']),
            "Date": get_date_time()
        }

        self.url = self.url + '?next=' + cursor + '&subscription=basic'

        response = requests.get(url=self.url, headers=head)

        obj = xmltodict.parse(response.content)
        return {"onix": obj, "cursor": response.headers['next']}
