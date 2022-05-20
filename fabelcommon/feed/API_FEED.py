import json
from typing import List, Dict
import requests
from xml.etree.ElementTree import Element, SubElement
from fabelcommon.datetime.time_formats import TimeFormats
from fabelcommon.bokbasen.CODELIST_BOKBASEN_METADATA import Bokgrupper, Varegrupper


class Auth():
    def __init__(self, username, password):
        self.url = "https://lydbokforlaget-feed.isysnet.no/token-server/oauth/token"
        self.username = username
        self.password = password

    def get_access_token(self) -> Dict:
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.url, data=data, verify=True, allow_redirects=False, auth=(self.username, self.password))
        if response.status_code == 200:
            response = json.loads(response.text)
            token = {
                'access_token': response['access_token']
            }
            return token
        raise Exception(f'Failed to retrieve token: status code {response.status_code}')


class Export():
    def __init__(self):
        self.base_url = 'https://lydbokforlaget-feed.isysnet.no/export/export?&changesOnly=false&size=500&productTypeImportCodes=ERP&'

    def set_head(self, access_token):
        head = {
            'Authorization': 'bearer {}'.format(access_token),
            'Content-Type': 'application/json'
        }
        return head

    def set_data(self, import_code, values):

        data = {
            'attributes': []
        }
        attributes = data['attributes']

        values_split = values.split(",")
        for value in values_split:
            attribute = {
                'importCode': import_code,
                'value': value.strip()}
            attributes.append(attribute)

        data = json.dumps(data)
        return data

    def export_full_by_page(self, access_token, page):
        head = self.set_head(access_token)
        url = self.base_url + 'page=' + str(page)
        response = requests.post(url, headers=head)
        if response.status_code == 200:
            response_data = response.json()
            response_books = response_data['content']
            if response_books:
                return response_books
            return {
                'error': 'not able to retrieve books'
            }
        raise Exception("f'Failed to get list of books: status code {response.status_code}'")

    def export_changes_by_page(self, access_token, page, hours):
        head = self.set_head(access_token)
        time = TimeFormats.get_time_delta_hours(hours)
        url = self.base_url + 'page=' + str(page) + '&exportFrom=' + str(time)
        response = requests.post(url, headers=head)

        if response.status_code == 200:
            response_data = response.json()
            response_books = response_data['content']
            if not response_books:
                response = {
                    'error': 'not able to retrieve books'
                }
                return response
            else:
                return response_books
        else:
            response = {
                'error': 'not able to retrieve books'
            }
            return response

    def export_by_isbn(self, access_token, isbn):
        head = self.set_head(access_token)
        data = self.set_data('lydfil-isbn', isbn)
        url = self.base_url + 'page=0'
        response = requests.post(url, headers=head, data=data)

        if response.status_code == 200:
            response_data = response.json()
            response_books = response_data['content']
            if not response_books:
                response = {
                    'error': 'not able to retrieve books'
                }
                return response
            else:
                return response_books
        else:
            response = {
                'error': 'not able to retrieve books'
            }

    def export_by_importcode_value(self, access_token, import_code, value, page):

        head = self.set_head(access_token)
        data = self.set_data(import_code, value)
        url = self.base_url + 'page=' + str(page)
        response = requests.post(url, headers=head, data=data)
        if response.status_code == 200:
            response_data = response.json()
            response_books = response_data['content']
            if response_books:
                return response_books
            return {
                'error': 'not able to retrieve books'
            }
        raise Exception(f'Could not retrieve books: status code {response.status_code}')

    def export_changes_by_importcode_value(self, access_token, import_code, value, page, hours):
        head = self.set_head(access_token)
        data = self.set_data(import_code, value)
        time = TimeFormats.get_time_delta_hours(hours)
        url = self.base_url + 'page=' + str(page) + '&exportFrom=' + str(time)

        response = requests.post(url, headers=head, data=data)
        response_error = {
            'error': 'not able to retrieve books'
        }

        if response.status_code != 200:
            return response_error

        response_data = response.json()
        response_books = response_data['content']

        if not response_books:
            return response_error

        return response_books

    def export_author_by_import_code(self, access_token, import_code) -> List[Dict]:
        head = self.set_head(access_token)
        url = 'https://lydbokforlaget-feed.isysnet.no//export/export?importCodes=' + import_code + '&size=500&changesOnly=false&page=0'
        response = requests.post(url, headers=head)
        if response.status_code == 200:
            response_data = response.json()
            response_author = response_data['content']
            return response_author
        return []


class Import():
    def __init__(self):
        self.base_url = 'https://lydbokforlaget-feed.isysnet.no//import/import'

    def set_head(self, access_token):
        head = {
            'Authorization': 'bearer {}'.format(access_token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return head

    def import_from_import_data(self, importdata, access_token):
        head = self.set_head(access_token)
        url = self.base_url
        data = json.dumps(importdata)
        response = requests.post(url, headers=head, data=data)
        if response.status_code == 200:
            response = {
                'success': response.text
            }
            return response
        else:
            response = {
                'error': response.text
            }
            return response

    def import_from_bokbasen(self, importdata, access_token):
        head = self.set_head(access_token)
        url = self.base_url
        data = json.dumps(importdata)
        response = requests.post(url, headers=head, data=data)
        if response.status_code == 200:
            response = {
                'success': response.text
            }
            return response
        else:
            response = {
                'error': response.text
            }
            return response


class Transform():
    def __init__(self):
        pass

    def get_attribute(self, bookitem, key, attribute, import_code, data_type="string"):
        if data_type == "string":
            if attribute['importCode'] == import_code:
                if 'nb' in attribute['value']:
                    bookitem[key] = attribute['value']['nb']
        elif data_type == "tags":
            if attribute['importCode'] == import_code:
                if 'value' in attribute:
                    for tag in attribute['value']:
                        bookitem["Tags"].append(tag)
        elif data_type == "nyhet":
            if attribute['importCode'] == import_code:
                if 'value' in attribute:
                    if attribute['value']:
                        bookitem['Tags'].append("Nyhet")

        elif data_type == "tilbud":
            if attribute['importCode'] == import_code:
                if 'value' in attribute:
                    if attribute['value']:
                        bookitem['Tags'].append("Tilbud")
        elif data_type == "date":
            if attribute['importCode'] == import_code:
                if 'value' in attribute:
                    bookitem[key] = TimeFormats.format_date_time_string(attribute['value'])

        elif data_type == 'dataregister-forlag':
            if attribute['importCode'] == import_code:
                if 'value' in attribute:
                    code = attribute['value']
                    forlag = attribute['options'][code]['nb']
                    bookitem[key] = forlag

        else:
            if attribute['importCode'] == import_code:
                if 'value' in attribute:
                    bookitem[key] = attribute['value']
        return bookitem

    def create_book_object_wpallimport_new(self, feed_json, access_token):
        if isinstance(feed_json, list):
            feed_json = feed_json[0]

        bookitem = {
            "ISBN": feed_json['productHead']['productNo'],
            "Tittel": feed_json['productHead']['name']['nb'],
            "Serietittel": "",
            "Serienummer": "",
            "Personer": [],
            "Pris": "",
            "Kampanjepris": "",
            "Kampanjepris_dato": [0, 0],
            "Format": "LYDFIL",
            "Sjanger": "",
            "Undersjanger": "",
            "Status format": "",
            "Abonnementsstatus": "",
            "Spilletid": "",
            "Utgivelsesdato": "",
            "Markedstekst": "",
            "Maalform": "",
            "Alder": "",
            "Lettlest": "",
            "Produsert_av": "",
            "Pocketpris": "",
            "Singelnovelle": "",
            "Forlag": '',
            "Fabel-ID": "",
            "Tags": [],
        }

        attributes = feed_json['attributes']
        texts = feed_json['texts']
        use_bokbasen_data = False
        use_bokbasen_purchase_data = False

        for attribute in attributes:
            if 'importCode' in attribute:
                if attribute['importCode'] == 'bokbasen-ny':
                    if 'value' in attribute:
                        if attribute['value']:
                            use_bokbasen_data = True

                if attribute['importCode'] == 'bokbasen-salgsinformasjon':
                    if 'value' in attribute:
                        if attribute['value']:
                            use_bokbasen_purchase_data = True

        if use_bokbasen_data:
            for attribute in attributes:
                if 'importCode' in attribute:
                    bookitem = self.get_attribute(bookitem, 'Serienummer', attribute, 'bokbasen-seriedel', "int")
                    bookitem = self.get_attribute(bookitem, 'Serietittel', attribute, 'bokbasen-serietittel')
                    bookitem = self.get_attribute(bookitem, 'Pris', attribute, 'bokbasen-pris')
                    bookitem = self.get_attribute(bookitem, 'Kampanjepris', attribute, 'lydfil-kampanjepris', 'int')
                    bookitem = self.get_attribute(bookitem, 'Kampanjepris_dato', attribute, 'lydfil_kampanjeprisdato', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Sjanger', attribute, 'hovedsjanger', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'barn', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'ungdom', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'faktaogdokumentar', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'skjonnliteratur', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Abonnementsstatus', attribute, 'lydfil-abbstatus', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Spilletid', attribute, 'bokbasen-varighet')
                    bookitem = self.get_attribute(bookitem, 'Utgivelsesdato', attribute, 'bokbasen-utgivelsesdato', 'date')
                    bookitem = self.get_attribute(bookitem, 'Maalform', attribute, 'bokbasen-målform')
                    bookitem = self.get_attribute(bookitem, 'Alder', attribute, 'bokbasen-malgruppe')
                    bookitem = self.get_attribute(bookitem, 'Produsert_av', attribute, 'bokbasen-produsent')
                    bookitem = self.get_attribute(bookitem, 'Forlag', attribute, 'bokbasen-forlag')
                    bookitem = self.get_attribute(bookitem, 'Fabel-ID', attribute, 'fabel-id', 'int')
                    bookitem = self.get_attribute(bookitem, 'Tags', attribute, 'stikkord-web', 'tags')
                    bookitem = self.get_attribute(bookitem, 'Tags', attribute, 'nyhet', 'nyhet')
                    bookitem = self.get_attribute(bookitem, 'Tags', attribute, 'tilbud', 'tilbud')

                    if attribute['importCode'] == 'bokbasen-forfatter':
                        if 'nb' in attribute['value']:
                            forfattere = attribute['value']['nb'].split(',')
                            for forfatter in forfattere:
                                bookitem['Personer'].append({
                                    "Fornavn": forfatter,
                                    "Etternavn": "",
                                    "Rolle": "Forfatter"
                                })
                    if attribute['importCode'] == 'bokbasen-innleser':
                        if 'nb' in attribute['value']:
                            innlesere = attribute['value']['nb'].split(',')
                            for innleser in innlesere:
                                bookitem['Personer'].append({
                                    "Fornavn": innleser,
                                    "Etternavn": "",
                                    "Rolle": "Innleser"
                                })

                    if attribute['importCode'] == 'bokbasen-oversetter':
                        if 'nb' in attribute['value']:
                            oversettere = attribute['value']['nb'].split(',')
                            for oversetter in oversettere:
                                bookitem['Personer'].append({
                                    "Fornavn": oversetter,
                                    "Etternavn": "",
                                    "Rolle": "Oversetter"
                                })
                    if use_bokbasen_purchase_data:
                        bookitem = self.get_attribute(bookitem, 'Status format', attribute, 'bokbasen-salgsstatus', 'dataregister')
                    else:
                        bookitem = self.get_attribute(bookitem, 'Status format', attribute, 'lydfil-salgsstatus', 'dataregister')
            for text in texts:
                if 'importCode' in text:
                    bookitem = self.get_attribute(bookitem, 'Markedstekst', text, 'salgstekst_lang')

            if bookitem['Pris'] != "":
                bookitem['Pris'] = bookitem['Pris'][:len(bookitem['Pris']) - 3]

            if bookitem['Kampanjepris_dato'][0] != 0:
                bookitem['Kampanjepris_dato'][0] = TimeFormats.format_date_time_string(bookitem['Kampanjepris_dato'][0])
                bookitem['Kampanjepris_dato'][1] = TimeFormats.format_date_time_string(bookitem['Kampanjepris_dato'][1])
        else:
            for attribute in attributes:
                if 'importCode' in attribute:
                    bookitem = self.get_attribute(bookitem, 'Serienummer', attribute, 'lydfil-serienummer', "int")
                    bookitem = self.get_attribute(bookitem, 'Serietittel', attribute, 'Serietittel-sok')
                    bookitem = self.get_attribute(bookitem, 'Pris', attribute, 'lydfil-pris', 'int')
                    bookitem = self.get_attribute(bookitem, 'Kampanjepris', attribute, 'lydfil-kampanjepris', 'int')
                    bookitem = self.get_attribute(bookitem, 'Kampanjepris_dato', attribute, 'lydfil_kampanjeprisdato', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Sjanger', attribute, 'hovedsjanger', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'barn', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'ungdom', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'faktaogdokumentar', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Undersjanger', attribute, 'skjonnliteratur', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Abonnementsstatus', attribute, 'lydfil-abbstatus', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Spilletid', attribute, 'lydfil-spilletid')
                    bookitem = self.get_attribute(bookitem, 'Utgivelsesdato', attribute, 'lydfil-utgivelsesdato', 'date')
                    bookitem = self.get_attribute(bookitem, 'Maalform', attribute, 'lydfil-maalform', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Alder', attribute, 'lydfil-alder', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Produsert_av', attribute, 'lydfil-produsertav', 'dataregister')
                    bookitem = self.get_attribute(bookitem, 'Forlag', attribute, 'lydfil-bokforlag', 'dataregister-forlag')
                    bookitem = self.get_attribute(bookitem, 'Fabel-ID', attribute, 'fabel-id', 'int')
                    bookitem = self.get_attribute(bookitem, 'Tags', attribute, 'stikkord-web', 'tags')
                    bookitem = self.get_attribute(bookitem, 'Tags', attribute, 'nyhet', 'nyhet')
                    bookitem = self.get_attribute(bookitem, 'Tags', attribute, 'tilbud', 'tilbud')

                    if use_bokbasen_purchase_data:
                        bookitem = self.get_attribute(bookitem, 'Status format', attribute, 'bokbasen-salgsstatus', 'dataregister')
                    else:
                        bookitem = self.get_attribute(bookitem, 'Status format', attribute, 'lydfil-salgsstatus', 'dataregister')

            for text in texts:
                if 'importCode' in text:
                    bookitem = self.get_attribute(bookitem, 'Markedstekst', text, 'salgstekst_lang')

            forfatter = 0
            innleser = 0
            oversetter = 0
            for relation in feed_json['relations']:

                if relation['relationTypeSortNo'] == 1:
                    forfatter += 1
                elif relation['relationTypeSortNo'] == 2:
                    innleser += 1
                elif relation['relationTypeSortNo'] == 4:
                    oversetter += 1
            if forfatter > 1:
                for relation in feed_json['relations']:
                    if relation['relationTypeSortNo'] == 1:
                        personobj = {}
                        importcode = relation['productImportCode']
                        lookup = Export().export_author_by_import_code(access_token, importcode)
                        if lookup:
                            name = lookup[0]['productHead']['name']['nb'].split(' ')
                            personobj['Etternavn'] = ' '.join(name[1:])
                            personobj['Fornavn'] = name[0]
                            personobj['Rolle'] = "Forfatter"
                            bookitem['Personer'].append(personobj)
                        else:
                            pass
            else:
                try:
                    person = feed_json['attributes'][17]['value']['nb'].split(' ')
                    if person[0] != '':
                        personobj = {}
                        personobj['Etternavn'] = ' '.join(person[1:])
                        personobj['Fornavn'] = person[0]
                        personobj['Rolle'] = "Forfatter"
                        bookitem['Personer'].append(personobj)
                except KeyError:
                    pass

            if innleser > 1:
                for relation in feed_json['relations']:
                    if relation['relationTypeSortNo'] == 2:
                        personobj = {}
                        importcode = relation['productImportCode']
                        lookup = Export().export_author_by_import_code(access_token, importcode)
                        name = lookup[0]['productHead']['name']['nb'].split(' ')
                        personobj['Etternavn'] = ' '.join(name[1:])
                        personobj['Fornavn'] = name[0]
                        personobj['Rolle'] = "Innleser"
                        bookitem['Personer'].append(personobj)
            else:
                try:
                    person = feed_json['attributes'][18]['value']['nb'].split(' ')
                    if person[0] != '':
                        personobj = {}
                        personobj['Etternavn'] = ' '.join(person[1:])
                        personobj['Fornavn'] = person[0]
                        personobj['Rolle'] = "Innleser"
                        bookitem['Personer'].append(personobj)
                except KeyError:
                    pass

            if oversetter > 1:
                for relation in feed_json['relations']:
                    if relation['relationTypeSortNo'] == 4:
                        personobj = {}
                        importcode = relation['productImportCode']
                        lookup = Export().export_author_by_import_code(access_token, importcode)
                        name = lookup[0]['productHead']['name']['nb'].split(' ')
                        personobj['Etternavn'] = ' '.join(name[1:])
                        personobj['Fornavn'] = name[0]
                        personobj['Rolle'] = "Oversetter"
                        bookitem['Personer'].append(personobj)
            else:
                try:
                    person = feed_json['attributes'][19]['value']['nb'].split(' ')
                    if person[0] != '':
                        personobj = {}
                        personobj['Etternavn'] = ' '.join(person[1:])
                        personobj['Fornavn'] = person[0]
                        personobj['Rolle'] = "Oversetter"
                        bookitem['Personer'].append(personobj)
                except KeyError:
                    pass

        return bookitem

    def create_book_object_wpallimport(self, feed_json, access_token):
        if isinstance(feed_json, list):
            feed_json = feed_json[0]
        bookitem = {
            "ISBN": feed_json['productHead']['productNo'],
            "Tittel": feed_json['productHead']['name']['nb'],
            "Serietittel": "",
            "Serienummer": "",
            "Personer": [],
            "Pris": "",
            "Kampanjepris": "",
            "Kampanjepris_dato": [0, 0],
            "Format": "LYDFIL",
            "Sjanger": "",
            "Undersjanger": "",
            "Status format": "",
            "Abonnementsstatus": "",
            "Spilletid": "",
            "Utgivelsesdato": "",
            "Markedstekst": "",
            "Maalform": "",
            "Alder": "",
            "Lettlest": "",
            "Produsert_av": "",
            "Pocketpris": "",
            "Singelnovelle": "",
            "Forlag": '',
            "Fabel-ID": "",
            "Tags": "",
        }

        if 'value' in feed_json['attributes'][1]:
            try:
                bookitem['Originaltittel'] = feed_json['attributes'][1]['value']['nb']
            except KeyError:
                bookitem['Originaltittel'] = ""

        if 'value' in feed_json['attributes'][2]:
            bookitem['Status format'] = feed_json['attributes'][2]['value']

        if 'value' in feed_json['attributes'][3]:
            bookitem['Abonnementsstatus'] = feed_json['attributes'][3]['value']

        purchase_subscription_attribute = ""
        if bookitem['Status format'] == "I salg":
            purchase_subscription_attribute += "Kjøp"
            if bookitem['Abonnementsstatus'] == "Aktiv":
                purchase_subscription_attribute += " | Abonnement"
        else:
            if bookitem['Abonnementsstatus'] == "Aktiv":
                purchase_subscription_attribute += "Abonnement"

        bookitem['purchase_subscription_attribute'] = purchase_subscription_attribute

        if 'value' in feed_json['attributes'][4]:
            bookitem['Alder'] = feed_json['attributes'][4]['value']

        if 'value' in feed_json['attributes'][5]:
            try:
                bookitem['Spilletid'] = feed_json['attributes'][5]['value']['nb']
            except KeyError:
                bookitem['Spilletid'] = ""

        if 'value' in feed_json['attributes'][6]:
            maalform = feed_json['attributes'][6]['value']
            if maalform == 'No-nb':
                bookitem['Maalform'] = "Bokmål"
            elif maalform == "No-nn":
                bookitem['Maalform'] = "Nynorsk"
            elif maalform == "eng":
                bookitem['Maalform'] = "Engelsk"
            elif maalform == "sme":
                bookitem['Maalform'] = "Samisk"

        if 'value' in feed_json['attributes'][7]:
            bookitem['Pris'] = feed_json['attributes'][7]['value']

        if 'value' in feed_json['attributes'][8]:
            bookitem['Kampanjepris'] = feed_json['attributes'][8]['value']

        if 'value' in feed_json['attributes'][9]:
            kampanjepris = feed_json['attributes'][9]['value']
            bookitem['Kampanjepris_dato'][0] = TimeFormats.format_date_time_string(kampanjepris[0])
            bookitem['Kampanjepris_dato'][1] = TimeFormats.format_date_time_string(kampanjepris[1])

        if 'value' in feed_json['attributes'][11]:
            bookitem['Produsert_av'] = feed_json['attributes'][11]['value']

        if 'value' in feed_json['attributes'][14]:
            bookitem['Utgivelsesdato'] = TimeFormats.format_date_time_string(feed_json['attributes'][14]['value'])

        if 'value' in feed_json['attributes'][16]:
            lydbokforlagkode = feed_json['attributes'][16]['value']
            lydbokforlag = feed_json['attributes'][16]['options'][lydbokforlagkode]['nb']
            bookitem['Forlag'] = lydbokforlag

        print(feed_json['productHead']['productNo'])

        hovedsjanger = feed_json['attributes'][22].get('value')
        undersjanger = ""

        if hovedsjanger == 'Skjønnlitteratur':
            undersjanger_kode = feed_json['attributes'][26]['value']
            try:
                undersjanger = feed_json['attributes'][26]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""
        elif hovedsjanger == 'Barn':
            undersjanger_kode = feed_json['attributes'][23]['value']
            try:
                undersjanger = feed_json['attributes'][23]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""
        elif hovedsjanger == 'Ungdom':
            undersjanger_kode = feed_json['attributes'][24]['value']
            try:
                undersjanger = feed_json['attributes'][24]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""
        elif hovedsjanger == 'Fakta og dokumentar':
            undersjanger_kode = feed_json['attributes'][25]['value']
            try:
                undersjanger = feed_json['attributes'][25]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""

        bookitem['Sjanger'] = hovedsjanger
        bookitem['Undersjanger'] = undersjanger

        if 'value' in feed_json['attributes'][27]:
            bookitem['Fabel-ID'] = str(feed_json['attributes'][27]['value'])

        try:
            bookitem['SEO-tittel'] = feed_json['attributes'][28]['value']['nb']
        except KeyError:
            bookitem['SEO-tittel'] = ""

        try:
            bookitem['metabeskrivelse'] = feed_json['attributes'][29]['value']['nb']
        except KeyError:
            bookitem['metabeskrivelse'] = ""

        tilbud = ""
        nyheter = ""
        redactional_tags = ""
        if 'value' in feed_json['attributes'][30]:
            redactional_tags = ', '.join(feed_json['attributes'][30]['value'])
            bookitem['Tags'] = redactional_tags

        if 'value' in feed_json['attributes'][31]:
            if feed_json['attributes'][31]['value']:
                tilbud = 'Tilbud'

        if 'value' in feed_json['attributes'][32]:
            if feed_json['attributes'][32]['value']:
                nyheter = "Nyheter"

        automatic_tags = nyheter + ', ' + tilbud
        bookitem['Tags'] = redactional_tags + ', ' + automatic_tags

        if 'value' in feed_json['texts'][1]:
            try:
                bookitem['Markedstekst'] = feed_json['texts'][1]['value']['nb']
            except KeyError:
                pass

        forfatter = 0
        innleser = 0
        oversetter = 0
        for relation in feed_json['relations']:

            if relation['relationTypeSortNo'] == 1:
                forfatter += 1
            elif relation['relationTypeSortNo'] == 2:
                innleser += 1
            elif relation['relationTypeSortNo'] == 4:
                oversetter += 1
        if forfatter > 1:
            for relation in feed_json['relations']:
                if relation['relationTypeSortNo'] == 1:
                    personobj = {}
                    importcode = relation['productImportCode']
                    lookup = Export().export_author_by_import_code(access_token, importcode)
                    if lookup:
                        name = lookup[0]['productHead']['name']['nb'].split(' ')
                        personobj['Etternavn'] = ' '.join(name[1:])
                        personobj['Fornavn'] = name[0]
                        personobj['Rolle'] = "Forfatter"
                        bookitem['Personer'].append(personobj)
                    else:
                        pass
        else:
            try:
                person = feed_json['attributes'][17]['value']['nb'].split(' ')
                if person[0] != '':
                    personobj = {}
                    personobj['Etternavn'] = ' '.join(person[1:])
                    personobj['Fornavn'] = person[0]
                    personobj['Rolle'] = "Forfatter"
                    bookitem['Personer'].append(personobj)
            except KeyError:
                pass

        if innleser > 1:
            for relation in feed_json['relations']:
                if relation['relationTypeSortNo'] == 2:
                    personobj = {}
                    importcode = relation['productImportCode']
                    lookup = Export().export_author_by_import_code(access_token, importcode)
                    name = lookup[0]['productHead']['name']['nb'].split(' ')
                    personobj['Etternavn'] = ' '.join(name[1:])
                    personobj['Fornavn'] = name[0]
                    personobj['Rolle'] = "Innleser"
                    bookitem['Personer'].append(personobj)
        else:
            try:
                person = feed_json['attributes'][18]['value']['nb'].split(' ')
                if person[0] != '':
                    personobj = {}
                    personobj['Etternavn'] = ' '.join(person[1:])
                    personobj['Fornavn'] = person[0]
                    personobj['Rolle'] = "Innleser"
                    bookitem['Personer'].append(personobj)
            except KeyError:
                pass

        if oversetter > 1:
            for relation in feed_json['relations']:
                if relation['relationTypeSortNo'] == 4:
                    personobj = {}
                    importcode = relation['productImportCode']
                    lookup = Export().export_author_by_import_code(access_token, importcode)
                    name = lookup[0]['productHead']['name']['nb'].split(' ')
                    personobj['Etternavn'] = ' '.join(name[1:])
                    personobj['Fornavn'] = name[0]
                    personobj['Rolle'] = "Oversetter"
                    bookitem['Personer'].append(personobj)
        else:
            try:
                person = feed_json['attributes'][19]['value']['nb'].split(' ')
                if person[0] != '':
                    personobj = {}
                    personobj['Etternavn'] = ' '.join(person[1:])
                    personobj['Fornavn'] = person[0]
                    personobj['Rolle'] = "Oversetter"
                    bookitem['Personer'].append(personobj)
            except KeyError:
                pass

        return bookitem

    def create_bookitem_simplified_tags(self, feed_json):
        bookitem = {
            "ISBN": feed_json['productHead']['productNo'],
            "Kampanjepris_dato": [0, 0]

        }

        if 'value' in feed_json['attributes'][8]:
            bookitem['Kampanjepris'] = feed_json['attributes'][8]['value']

        if 'value' in feed_json['attributes'][9]:
            kampanjepris = feed_json['attributes'][9]['value']
            try:
                bookitem['Kampanjepris_dato'][0] = TimeFormats.format_date_time_string(kampanjepris[0])
                bookitem['Kampanjepris_dato'][1] = TimeFormats.format_date_time_string(kampanjepris[1])
            except KeyError:
                pass

        if 'value' in feed_json['attributes'][14]:
            bookitem['Utgivelsesdato'] = TimeFormats.format_date_time_string(feed_json['attributes'][14]['value'])

        if 'value' in feed_json['attributes'][31]:
            if feed_json['attributes'][31]['value']:
                bookitem['Tilbud'] = True
            else:
                bookitem['Tilbud'] = False
        else:
            bookitem['Tilbud'] = False

        if 'value' in feed_json['attributes'][32]:
            if feed_json['attributes'][32]['value']:
                bookitem['Nyhet'] = True
            else:
                bookitem['Nyhet'] = False
        else:
            bookitem['Nyhet'] = False

        return bookitem

    def create_book_item_solr(self, feed_json, access_token):
        bookitem = {
            "itemid": feed_json['productHead']['productNo'],
            "title": feed_json['productHead']['name']['nb'],
            "description": "",
            "author": [],
            "narrator": [],
            "series_name": "",
            "category": [],
            "genre": ["", ""],
            "language": "",
            "duration_minutes": "",
            "price": "",
            "streamable": "",
            "purchasable": "",
            "channel": "audio",
            "published_date": "",
            "published_year": "",
            "fabel-id": "",
            "produced_by": "",
            "publisher": ""
        }

        if 'value' in feed_json['attributes'][14]:
            bookitem['published_date'] = TimeFormats.format_date_time_string_utc(feed_json['attributes'][14]['value'])
            bookitem['published_year'] = int(TimeFormats.format_date_time_string_utc(feed_json['attributes'][14]['value'])[:4])

        if 'value' in feed_json['attributes'][7]:
            bookitem['price'] = feed_json['attributes'][7]['value']

        if 'value' in feed_json['attributes'][22]:
            bookitem['genre'][0] = feed_json['attributes'][22]['value']

        if 'value' in feed_json['attributes'][22]:
            bookitem['genre'][1] = feed_json['attributes'][22]['value']

        try:
            if 'value' in feed_json['attributes'][20]:
                bookitem['series_name'] = feed_json['attributes'][20]['value']['nb']
        except KeyError:
            pass

        if 'value' in feed_json['texts'][1]:
            try:
                bookitem['description'] = feed_json['texts'][1]['value']['nb']
            except KeyError:
                pass

        if 'value' in feed_json['attributes'][3]:
            bookitem['streamable'] = feed_json['attributes'][3]['value']

        if 'value' in feed_json['attributes'][2]:
            bookitem['purchasable'] = feed_json['attributes'][2]['value']

        if bookitem['streamable'] == 'Aktiv':
            bookitem['streamable'] = True

        else:
            bookitem['streamable'] = False

        if bookitem['purchasable'] == 'I salg' or bookitem['purchasable'] == 'Kommer':
            bookitem['purchasable'] = True

        else:
            bookitem['purchasable'] = False

        if 'value' in feed_json['attributes'][27]:
            bookitem['fabel-id'] = str(feed_json['attributes'][27]['value'])

        if 'value' in feed_json['attributes'][5]:
            try:
                if feed_json['attributes'][5]['value']['nb'] != "":
                    bookitem['duration_minutes'] = TimeFormats.convert_to_minutes(feed_json['attributes'][5]['value']['nb'])
                else:
                    bookitem.pop('duration_minutes', None)
            except KeyError:
                pass

        if 'value' in feed_json['attributes'][4]:
            bookitem['age'] = feed_json['attributes'][4]['value']

        if 'value' in feed_json['attributes'][16]:
            lydbokforlagkode = feed_json['attributes'][16]['value']
            lydbokforlag = feed_json['attributes'][16]['options'][lydbokforlagkode]['nb']
            bookitem['publisher'] = lydbokforlag

        if 'value' in feed_json['attributes'][11]:
            bookitem['produced_by'] = feed_json['attributes'][11]['value']

        hovedsjanger = feed_json['attributes'][22]['value']
        undersjanger = 'initial_value'
        if hovedsjanger == 'Skjønnlitteratur':
            undersjanger_kode = feed_json['attributes'][26]['value']
            try:
                undersjanger = feed_json['attributes'][26]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""
        elif hovedsjanger == 'Barn':
            undersjanger_kode = feed_json['attributes'][23]['value']
            try:
                undersjanger = feed_json['attributes'][23]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""
        elif hovedsjanger == 'Ungdom':
            undersjanger_kode = feed_json['attributes'][24]['value']
            try:
                undersjanger = feed_json['attributes'][24]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""
        elif hovedsjanger == 'Fakta og dokumentar':
            undersjanger_kode = feed_json['attributes'][25]['value']
            try:
                undersjanger = feed_json['attributes'][25]['options'][undersjanger_kode[0]]['nb']
            except IndexError:
                undersjanger = ""

        if undersjanger == 'initial_value':
            raise Exception(f'Unhandled genre: {hovedsjanger}; subgenre not set')

        bookitem['genre'][0] = hovedsjanger
        bookitem['genre'][1] = undersjanger

        if 'value' in feed_json['attributes'][6]:
            maalform = feed_json['attributes'][6]['value']
            if maalform == 'No-nb':
                bookitem['language'] = "Bokmål"
            elif maalform == "No-nn":
                bookitem['language'] = "Nynorsk"
            elif maalform == "eng":
                bookitem['language'] = "Engelsk"
            elif maalform == "sme":
                bookitem['language'] = "Samisk"

        persontypes = ['Forfatter', 'Innleser', 'Oversetter']

        for i in range(len(persontypes)):
            if 'value' in feed_json['attributes'][17]:
                try:
                    person = feed_json['attributes'][17 + i]['value']['nb'].split(' ')
                    if person[0] != '':
                        personqueryparam = ''
                        for navn in person:
                            personqueryparam += navn + " "
                        personqueryparam = personqueryparam[:-1]

                        if persontypes[i] == "Forfatter":
                            bookitem['author'].append(personqueryparam)
                        elif persontypes[i] == "Innleser":
                            bookitem['narrator'].append(personqueryparam)
                except KeyError:
                    pass
                else:
                    pass

        return bookitem

    def create_onix_beat_header(self, feed_json):
        root = Element('ONIXMessage')
        root.set('release', '3.0')
        root.set('xmlns', "http://ns.editeur.org/onix/3.0/reference")

        header = SubElement(root, 'Header')
        sender = SubElement(header, 'Sender')

        sender_name = SubElement(sender, 'SenderName')
        sender_name.text = "Lydbokforlaget AS"
        contact_name = SubElement(sender, "ContactName")
        contact_name.text = "Helge Bjørløw"
        email_adress = SubElement(header, 'EmailAdress')
        email_adress.text = "helge.bjorlow@lydbokforlaget.no"
        message_number = SubElement(root, "MessageNumber")
        message_number.text = "123"
        sent_date_time = SubElement(root, "SentDateTime")
        sent_date_time.text = TimeFormats.get_date_time()
        message_note = SubElement(root, "MessageNote")
        message_note.text = "Test Message"

        return root

    def create_onix_beat(self, feed_json, root):
        product = SubElement(root, 'Product')

        if isinstance(feed_json, list):
            feed_json = feed_json[0]

        attributes = feed_json['attributes']

        for attribute in attributes:

            if 'importCode' in attribute:
                if attribute['importCode'] == 'bokbasen-id':
                    if 'value' in attribute:
                        product_identifier = SubElement(product, 'ProductIdentifier')
                        product_id_type = SubElement(product_identifier, 'ProductIDType')
                        product_id_type.text = '06'
                        id_value = SubElement(product_identifier, 'IDValue')
                        id_value.text = str(attribute['value'])
                elif attribute['importCode'] == 'lydfil-isbn':
                    if 'value' in attribute:
                        product_identifier = SubElement(product, 'ProductIdentifier')
                        product_id_type = SubElement(product_identifier, 'ProductIDType')
                        product_id_type.text = '15'
                        id_value = SubElement(product_identifier, 'IDValue')
                        id_value.text = attribute['value']['nb']
                elif attribute['importCode'] == 'bokbasen-notification-type':
                    if 'nb' in attribute['value']:
                        notification_type = SubElement(product, 'NotificationType')
                        notification_type_value = attribute['value']['nb']
                        print(notification_type_value)
                        if notification_type_value == 'Notification confirmed':
                            notification_type.text = '03'
                        elif notification_type_value == 'Advance notification':
                            notification_type.text = '02'
                        elif notification_type_value == 'Early notification':
                            notification_type.text = '01'

        descriptive_detail = SubElement(product, 'DescriptiveDetail')
        collection_created = False
        contributor_sequence_number = 1

        publishing_detail = SubElement(product, 'PublishingDetail')
        product_supply = SubElement(product, 'ProductSupply')

        for attribute in attributes:
            if 'importCode' in attribute:
                if attribute['importCode'] == 'bokbasen-seriedel':
                    if 'value' in attribute:
                        if not collection_created:
                            collection = SubElement(descriptive_detail, 'Collection')
                            collection_type = SubElement(collection, 'CollectionType')
                            collection_type.text = '20'
                            title_detail_collection = SubElement(collection, 'TitleDetail')
                            title_type = SubElement(title_detail_collection, 'TitleType')
                            title_type.text = '01'
                            collection_created = True
                        # pyright analysis disabled - function create_onix_beat appears to be unused
                        title_element = SubElement(title_detail_collection, 'TitleElement')  # type: ignore
                        sequence_number = SubElement(title_element, 'SequenceNumber')
                        sequence_number.text = '3'
                        title_element_level = SubElement(title_element, 'TitleElementLevel')
                        title_element_level.text = '01'
                        part_number = SubElement(title_element, 'PartNumber')
                        part_number.text = str(attribute['value'])
                if attribute['importCode'] == 'bokbasen-serietittel':
                    if 'nb' in attribute['value']:
                        if not collection_created:
                            collection = SubElement(descriptive_detail, 'Collection')
                            collection_type = SubElement(collection, 'CollectionType')
                            collection_type.text = '20'
                            title_detail_collection = SubElement(collection, 'TitleDetail')
                            title_type = SubElement(title_detail_collection, 'TitleType')
                            title_type.text = '01'
                            collection_created = True
                        # pyright analysis disabled - function create_onix_beat appears to be unused
                        title_element = SubElement(title_detail_collection, 'TitleElement')  # type: ignore
                        sequence_number = SubElement(title_element, 'SequenceNumber')
                        sequence_number.text = '2'
                        title_element_level = SubElement(title_element, 'TitleElementLevel')
                        title_element_level.text = '02'
                        title_text = SubElement(title_element, 'TitleText')
                        title_text.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-tittel':
                    if 'nb' in attribute['value']:
                        title_detail = SubElement(descriptive_detail, 'TitleDetail')
                        title_type = SubElement(title_detail, 'TitleType')
                        title_type.text = '01'
                        title_element = SubElement(title_detail, 'TitleElement')
                        sequence_number = SubElement(title_element, 'SequenceNumber')
                        sequence_number.text = '1'
                        title_element_level = SubElement(title_element, 'TitleElementLevel')
                        title_element_level.text = '01'
                        title_text = SubElement(title_element, 'TitleText')
                        title_text.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-forfatter':
                    if 'nb' in attribute['value']:
                        contributor = SubElement(descriptive_detail, 'Contributor')
                        sequence_number = SubElement(contributor, 'SequenceNumber')
                        sequence_number.text = str(contributor_sequence_number)
                        contributor_sequence_number += 1
                        contributor_role = SubElement(contributor, 'ContributorRole')
                        contributor_role.text = 'A01'
                        person_name = SubElement(contributor, 'PersonName')
                        person_name.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-innleser':
                    if 'nb' in attribute['value']:
                        contributor = SubElement(descriptive_detail, 'Contributor')
                        sequence_number = SubElement(contributor, 'SequenceNumber')
                        sequence_number.text = str(contributor_sequence_number)
                        contributor_sequence_number += 1
                        contributor_role = SubElement(contributor, 'ContributorRole')
                        contributor_role.text = 'E07'
                        person_name = SubElement(contributor, 'PersonName')
                        person_name.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-oversetter':
                    if 'nb' in attribute['value']:
                        contributor = SubElement(descriptive_detail, 'Contributor')
                        sequence_number = SubElement(contributor, 'SequenceNumber')
                        sequence_number.text = str(contributor_sequence_number)
                        contributor_sequence_number += 1
                        contributor_role = SubElement(contributor, 'ContributorRole')
                        contributor_role.text = 'B06'
                        person_name = SubElement(contributor, 'PersonName')
                        person_name.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-målform':
                    if 'nb' in attribute['value']:
                        language = SubElement(descriptive_detail, 'Language')
                        print(attribute['value']['nb'])
                        if attribute['value']['nb'] == 'Norwegian Bokmål':
                            language_role = SubElement(language, 'LanguageRole')
                            language_role.text = '01'
                            language_code = SubElement(language, 'LanguageCode')
                            language_code.text = 'nob'
                        elif attribute['value']['nb'] == 'Norwegian Nynorsk':
                            language_role = SubElement(language, 'LanguageRole')
                            language_role.text = '01'
                            language_code = SubElement(language, 'LanguageCode')
                            language_code.text = 'nno'

                if attribute['importCode'] == 'bokbasen-varighet':
                    if 'nb' in attribute['value']:
                        extent = SubElement(descriptive_detail, 'Extent')
                        extent_type = SubElement(extent, 'ExtentType')
                        extent_type.text = '09'
                        extent_value = SubElement(extent, 'ExtentValue')
                        extent_value.text = attribute['value']['nb']
                        extent_unit = SubElement(extent, 'ExtentUnit')
                        extent_unit.text = '05'

                if attribute['importCode'] == 'bokbasen-bokgruppe':
                    if 'nb' in attribute['value']:
                        subject_bokgruppe = SubElement(descriptive_detail, 'Subject')
                        subject_id = SubElement(subject_bokgruppe, 'SubjectSchemeIdentifier')
                        subject_id.text = '37'
                        subject_code = SubElement(subject_bokgruppe, 'SubjectCode')
                        subject_code.text = list(Bokgrupper.keys())[list(Bokgrupper.values()).index(attribute['value']['nb'])]

                if attribute['importCode'] == 'bokbasen-varegruppe':
                    if 'nb' in attribute['value']:
                        subject_varegruppe = SubElement(descriptive_detail, 'Subject')
                        subject_id = SubElement(subject_varegruppe, 'SubjectSchemeIdentifier')
                        subject_id.text = '38'
                        subject_code = SubElement(subject_varegruppe, 'SubjectCode')
                        subject_code.text = list(Varegrupper.keys())[list(Varegrupper.values()).index(attribute['value']['nb'])]

                if attribute['importCode'] == 'bokbasen-thema':
                    if 'nb' in attribute['value']:
                        thema_classification = attribute['value']['nb']
                        thema_classification = thema_classification.split(',')
                        for thema in thema_classification:
                            subject_thema = SubElement(descriptive_detail, 'Subject')
                            subject_id = SubElement(subject_thema, 'SubjectSchemeIdentifier')
                            subject_id.text = '24'
                            subject_name = SubElement(subject_thema, 'SubjectName')
                            subject_name.text = 'Lydbokforlaget_Thema_Classification'
                            subject_text = SubElement(subject_thema, 'SubjectHeadingText')
                            subject_text.text = thema

                if attribute['importCode'] == 'bokbasen-sjanger':
                    if 'nb' in attribute['value']:
                        bokbasen_genre = attribute['value']['nb']
                        bokbasen_genre = bokbasen_genre.split(',')
                        for genre in bokbasen_genre:
                            subject_bokbasen = SubElement(descriptive_detail, 'Subject')
                            subject_id = SubElement(subject_bokbasen, 'SubjectSchemeIdentifier')
                            subject_id.text = '24'
                            subject_name = SubElement(subject_bokbasen, 'SubjectName')
                            subject_name.text = 'Lydbokforlaget_Bokbasen_Genre'
                            subject_text = SubElement(subject_bokbasen, 'SubjectHeadingText')
                            subject_text.text = genre

                if attribute['importCode'] == 'bokbasen-malgruppe':
                    if 'nb' in attribute['value']:
                        audience = SubElement(descriptive_detail, 'Audience')
                        audience_code_type = SubElement(audience, 'AudienceCodeType')
                        audience_code_type.text = "02"
                        audience_code_type_name = SubElement(audience, 'AudienceCodeTypeName')
                        audience_code_type_name.text = "Bokbasen_Audience"
                        audience_code_value = SubElement(audience, 'AudienceCodeValue')
                        audience_code_value.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-produsent':
                    if 'nb' in attribute['value']:
                        imprint = SubElement(publishing_detail, 'Imprint')
                        imprint_name = SubElement(imprint, 'ImprintName')
                        imprint_name.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-forlag':
                    if 'nb' in attribute['value']:
                        publisher = SubElement(publishing_detail, 'Publisher')
                        publisher_name = SubElement(publisher, 'PublisherName')
                        publisher_name.text = attribute['value']['nb']

                if attribute['importCode'] == 'bokbasen-utgivelsesdato':
                    if 'value' in attribute:
                        publishing_date = SubElement(publishing_detail, 'PublishingDate')
                        publishing_date_role = SubElement(publishing_date, 'PublishingDateRole')
                        publishing_date_role.text = "11"
                        date_format = SubElement(publishing_date, 'DateFormat')
                        date_format.text = "00"
                        date = SubElement(publishing_date, 'Date')
                        date.text = attribute['value'].replace('-', '')[0:8]

                if attribute['importCode'] == 'bokbasen-salgsinformasjon':
                    market = SubElement(product_supply, 'Market')
                    territory = SubElement(market, 'Territory')
                    territory.text = "Norway"
                    if 'value' in attribute:
                        if attribute['value']:
                            for attribute_sales in attributes:
                                if 'importCode' in attribute_sales:
                                    if attribute_sales['importCode'] == 'bokbasen-salgsstatus':
                                        if 'value' in attribute_sales:
                                            sales_restriction_purchase = SubElement(market, 'SalesRestrictionPurchase')
                                            sales_restriction_purchase.text = attribute_sales['value']
                                    if attribute_sales['importCode'] == 'bokbasen-abonnementstatus':
                                        if 'value' in attribute_sales:
                                            sales_restriction_streaming = SubElement(market, 'SalesRestrictionStreaming')
                                            sales_restriction_streaming.text = attribute_sales['value']

                        else:
                            for attribute_sales in attributes:
                                if 'importCode' in attribute_sales:
                                    if attribute_sales['importCode'] == 'lydfil-salgsstatus':
                                        if 'value' in attribute_sales:
                                            sales_restriction_purchase = SubElement(market, 'SalesRestrictionPurchase')
                                            sales_restriction_purchase.text = attribute_sales['value']
                                    if attribute_sales['importCode'] == 'lydfil-abbstatus':
                                        if 'value' in attribute_sales:
                                            sales_restriction_streaming = SubElement(market, 'SalesRestrictionStreaming')
                                            sales_restriction_streaming.text = attribute_sales['value']

                    else:
                        for attribute_sales in attributes:
                            if 'importCode' in attribute_sales:
                                if attribute_sales['importCode'] == 'lydfil-salgsstatus':
                                    if 'value' in attribute_sales:
                                        sales_restriction_purchase = SubElement(market, 'SalesRestrictionPurchase')
                                        sales_restriction_purchase.text = attribute_sales['value']
                                if attribute_sales['importCode'] == 'lydfil-abbstatus':
                                    if 'value' in attribute_sales:
                                        sales_restriction_streaming = SubElement(market, 'SalesRestrictionStreaming')
                                        sales_restriction_streaming.text = attribute_sales['value']

        return root
