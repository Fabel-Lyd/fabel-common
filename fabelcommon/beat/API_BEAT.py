import json
from typing import Dict
import requests
from collections import namedtuple
from rest_framework import status


BEAT_BASE_URL = 'https://api.fabel.no'
Result = namedtuple("Result", "is_success, error")


def create_headers(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    return headers


class Tokens:
    url = "https://api.fabel.no/v2/oauth2/token"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def password(self, msisdn, password):
        data = {
            'grant_type': 'password',
            'username': msisdn,
            'password': password,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(Tokens.url, data=data, verify=True, allow_redirects=False)

        if response.status_code == 200:

            response = json.loads(response.text)

            tokens = {
                'access_token': response['access_token'],
                'refresh_token': response['refresh_token'],
                'fabel_id': response['user_id']
            }

            return tokens

        return False

    def client(self) -> Dict:
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(Tokens.url, data=data, verify=True, allow_redirects=False)
        if response.status_code != 200:
            raise Exception(f'Failed to retrieve token: status code {response.status_code}')

        response_body = json.loads(response.text)
        return {
            'access_token': response_body['access_token']
        }

    def refresh_token(self, token):

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(Tokens.url, data=data, verify=True, allow_redirects=False)
        if response.status_code == 200:

            response = json.loads(response.text)

            token = {
                'access_token': response['access_token'],
            }

            return token

        return False


class User:

    def __init__(self, client_id, client_secret):
        self.beat_token = Tokens(client_id, client_secret).client().get('access_token')

    @staticmethod
    def get_user(fabel_id, token) -> Dict:
        headers = {'Authorization': 'Bearer ' + str(token)}
        url = 'https://api.fabel.no/v2/users/{}'.format(fabel_id)

        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        if response.status_code != 200:
            raise Exception(f'Failed to retrieve user: status code {response.status_code}')

        return json.loads(response.text)

    @staticmethod
    def update_user(data):
        headers = {
            'Authorization': 'Bearer ' + str(data['access_token']),
            'Content-Type': 'application/json'
        }
        token_url = 'https://api.fabel.no/v2/users/' + str(data['fabel_id'])

        filtered_data = {}
        for key, value in data.items():
            if key == 'firstname':
                filtered_data[key] = value
            if key == 'lastname':
                filtered_data[key] = value
            if key == 'email':
                filtered_data[key] = value
            if key == 'newsletter':
                filtered_data[key] = value
            if key == 'password':
                filtered_data[key] = value
            if key == 'payment_type':
                filtered_data[key] = value

        data = json.dumps(filtered_data)
        response = requests.patch(token_url, headers=headers, data=data, verify=True, allow_redirects=False)
        if response.status_code == 200:
            return True

        return False

    def exists_user(self, msisdn):
        headers = {'Authorization': 'Bearer ' + str(self.beat_token)}
        url = 'https://api.fabel.no/v2/users?msisdn=' + str(msisdn)
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        if response.status_code == 206:
            return json.loads(response.text)
        return False

    def create_user(self, data):
        headers = {
            'Authorization': 'Bearer ' + str(self.beat_token),
            'Content-Type': 'application/json'
        }
        url = 'https://api.fabel.no/v2/users'
        filtered_data = {}
        for key, value in data.items():
            if key == 'msisdn':
                filtered_data[key] = value
            if key == 'firstname':
                filtered_data[key] = value
            if key == 'lastname':
                filtered_data[key] = value
            if key == 'email':
                filtered_data[key] = value
            if key == 'newsletter':
                filtered_data[key] = value

        data = json.dumps(filtered_data)
        response = requests.post(url, headers=headers, data=data, verify=True, allow_redirects=False)
        if response.status_code == 201:
            return json.loads(response.text)['user']['id']
        return False


class SMS:

    def __init__(self, client_id, client_secret):
        self.beat_token = Tokens(client_id, client_secret).client().get('access_token')

    def password_request(self, msisdn):
        url = 'https://api.fabel.no/v2/passwords/requests'
        headers = {
            'Authorization': 'Bearer ' + str(self.beat_token),
            'Content-Type': 'application/json',
        }
        data = {'msisdn': msisdn}
        data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers, verify=True, allow_redirects=False)
        if response.status_code == 201:
            return True
        return False

    def password_verify(self, code, password, msisdn):
        headers = {'Authorization': 'Bearer ' + str(self.beat_token)}
        url = 'https://api.fabel.no/v2/passwords'
        data = {
            'msisdn': msisdn,
            'password': password,
            'code': code,
        }
        data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers, verify=True, allow_redirects=False)
        if response.status_code == 201:
            return True
        return False


class Email:

    def __init__(self, client_id, client_secret):
        self.beat_token = Tokens(client_id, client_secret).client().get('access_token')

    @staticmethod
    def credentials(email, fabel_id, token):
        url = 'https://api.fabel.no/v2/users/{}/credentials'.format(fabel_id)
        headers = {
            'Authorization': 'Bearer ' + str(token),
            'Content-Type': 'application/json',
        }
        data = {
            'type': 6,
            'credential': email
        }
        data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers, verify=True, allow_redirects=False)

        if response.status_code == 200:
            return True
        return False

    def credentials_verify(self, fabel_id, token_type, token):
        url = 'https://api.fabel.no/v2/users/{}/credentials/verifications'.format(fabel_id)
        headers = {
            'Authorization': 'Bearer ' + str(self.beat_token),
            'Content-Type': 'application/json',
        }
        data = {
            'token': token,
            'type': int(token_type),
        }
        data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers, verify=True, allow_redirects=False)
        if response.status_code == 201:
            return True
        return False


class SUB:

    @staticmethod
    def get(fabel_id, access_token):
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        url = 'https://api.fabel.no/v2/users/' + str(fabel_id) + '/subscriptions'
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        if status.is_success(response.status_code):
            response = json.loads(response.text).get('subscriptions')
            return response[0] if response else {}

        raise Exception('Error getting subscription.', response.text)

    @staticmethod
    def state(access_token, fabel_id, sub_id, state, cmt):
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        url = 'https://api.fabel.no/v2/users/{}/subscriptions/{}'.format(fabel_id, sub_id)
        data = {'state': int(state), 'comment': cmt}
        data = json.dumps(data)
        response = requests.patch(url, headers=headers, data=data, verify=True, allow_redirects=False)
        if response.status_code == 200:
            return json.loads(response.text)
        return False

    @staticmethod
    def migrate(data):
        headers = {
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }
        url = 'https://api.fabel.no/v2/users/{}/migrations'.format(data['fabel_id'])
        filtered_data = {}
        for key, value in data.items():
            if key == 'product_id':
                filtered_data[key] = str(value)
            if key == 'utm_campaign' and value != "":
                filtered_data[key] = value
            if key == 'renewable':
                filtered_data[key] = value
            if key == 'confirmed':
                filtered_data[key] = value
            # if key == 'metadata': filtered_data[key] = value
        data = json.dumps(filtered_data)
        response = requests.post(url, headers=headers, data=data, verify=True, allow_redirects=False)
        if response.status_code == 201:
            return True
        return False

    @staticmethod
    def get_balance(fabel_id, access_token):
        url = f'{BEAT_BASE_URL}/v2/users/{fabel_id}/balances'
        headers = create_headers(access_token)
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        balances = json.loads(response.text)['balances']
        return balances[0] if balances else {}

    @staticmethod
    def charge(data, access_token) -> Result:
        url = f'{BEAT_BASE_URL}/v2/charges'
        headers = create_headers(access_token)

        response = requests.post(url, headers=headers, data=json.dumps(data), verify=True, allow_redirects=False)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            return Result(is_success=True, error=None)

        if response.status_code == status.HTTP_403_FORBIDDEN:
            return Result(is_success=False, error=response.json()['error_description'])

        # need to introduce global error handling
        raise Exception('Error selecting a book.', response.text)

    @staticmethod
    def borrowed_releases(access_token):
        url = f'{BEAT_BASE_URL}/v2/releases/groups/borrowed/releases'
        headers = create_headers(access_token)

        get_response = requests.get(url, headers=headers, verify=True, allow_redirects=False)

        releases = [release.get('id') for release in get_response.json()['releases']]
        return releases


class Coupon:

    @staticmethod
    def redeem(fabel_id, access_token, coupon):
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        data = json.dumps({'coupon': coupon})
        url = 'https://api.fabel.no/v2/users/{}/coupons/redemptions'.format(fabel_id)
        response = requests.post(url, data=data, headers=headers, verify=True, allow_redirects=False)
        return response.status_code


class Payment:

    @staticmethod
    def stripe_setup_intents(access_token):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
        }
        token_url = 'https://api.fabel.no/v2/billing/setupintents'
        data = {
            'payment_type': 3
        }
        data = json.dumps(data)
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            return json.loads(response.text)
        return False

    @staticmethod
    def stripe_payment_methode(access_token, reference):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
        }
        token_url = 'https://api.fabel.no/v2/billing/paymentmethods'
        data = {
            'payment_type': 3,
            'reference': reference
        }
        data = json.dumps(data)
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            return json.loads(response.text)
        return False


class BEATAPI():

    def __init__(self):
        self.url = 'https://api.fabel.no/v2/releases/groups/1'

    def get_most_listen_to(self, access_token) -> Dict:
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json',
        }

        response = requests.get(self.url, headers=headers, verify=True, allow_redirects=False)

        if response.status_code == 200:
            response = json.loads(response.text)
            return response
        else:
            raise Exception(f'Failed to get list of books: status code {response.status_code}')

    def validate_file(self, xml):
        url = "https://ds.beat.delivery/v1/sources/onix"
        headers = {
            "Content-Type": "multipart/form-data, boundary=1000"
        }
        response = requests.post(url, data=xml, headers=headers)
        return response.text
