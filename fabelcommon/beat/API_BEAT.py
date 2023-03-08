import json
from typing import Dict
from urllib.parse import urljoin
import requests
from collections import namedtuple
from rest_framework import status

Result = namedtuple("Result", "is_success, error")


def create_headers(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    return headers


class Tokens:
    def __init__(self, client_id, client_secret, base_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url

    def password(self, msisdn, password):
        data = {
            'grant_type': 'password',
            'username': msisdn,
            'password': password,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(
            url=urljoin(self.base_url, '/v2/oauth2/token'),
            data=data,
            verify=True,
            allow_redirects=False)

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

        response = requests.post(
            url=urljoin(self.base_url, '/v2/oauth2/token'),
            data=data,
            verify=True,
            allow_redirects=False)
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

        response = requests.post(
            url=urljoin(self.base_url, '/v2/oauth2/token'),
            data=data,
            verify=True,
            allow_redirects=False)
        if response.status_code == 200:

            response = json.loads(response.text)

            token = {
                'access_token': response['access_token'],
            }

            return token

        return False


class User:

    def __init__(self, client_id, client_secret, base_url):
        self.beat_token = Tokens(client_id, client_secret, base_url).client().get('access_token')
        self.base_url = base_url

    @staticmethod
    def get_user(fabel_id, token, base_url) -> Dict:
        headers = {'Authorization': 'Bearer ' + str(token)}
        url = urljoin(base_url, f'/v2/users/{fabel_id}')

        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        if response.status_code != 200:
            raise Exception(f'Failed to retrieve user: status code {response.status_code}')

        return json.loads(response.text)

    @staticmethod
    def update_user(data, base_url):
        headers = {
            'Authorization': 'Bearer ' + str(data['access_token']),
            'Content-Type': 'application/json'
        }
        fabel_id = str(data['fabel_id'])
        token_url = urljoin(base_url, f'/v2/users/{fabel_id}')

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
        url = urljoin(self.base_url, f'/v2/users?msisdn={msisdn}')
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        if response.status_code == 206:
            return json.loads(response.text)
        return False

    def create_user(self, data):
        headers = {
            'Authorization': 'Bearer ' + str(self.beat_token),
            'Content-Type': 'application/json'
        }
        url = urljoin(self.base_url, '/v2/users')
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

    def __init__(self, client_id, client_secret, base_url):
        self.beat_token = Tokens(client_id, client_secret, base_url).client().get('access_token')
        self.base_url = base_url

    def password_request(self, msisdn):
        url = urljoin(self.base_url, '/v2/passwords/requests')
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
        url = urljoin(self.base_url, '/v2/passwords')
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

    def __init__(self, client_id, client_secret, base_url):
        self.beat_token = Tokens(client_id, client_secret, base_url).client().get('access_token')
        self.base_url = base_url

    @staticmethod
    def credentials(email, fabel_id, token, base_url):
        url = urljoin(base_url, f'/v2/users/{fabel_id}/credentials')
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
        url = urljoin(self.base_url, f'/v2/users/{fabel_id}/credentials/verifications')
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
    def get(fabel_id, access_token, base_url):
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        url = urljoin(base_url, f'/v2/users/{fabel_id}/subscriptions')
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        if status.is_success(response.status_code):
            response = json.loads(response.text).get('subscriptions')
            return response[0] if response else {}

        raise Exception('Error getting subscription.', response.text)

    @staticmethod
    def state(access_token, fabel_id, sub_id, state, cmt, base_url):
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        url = urljoin(base_url, f'/v2/users/{fabel_id}/subscriptions/{sub_id}')
        data = {'state': int(state), 'comment': cmt}
        data = json.dumps(data)
        response = requests.patch(url, headers=headers, data=data, verify=True, allow_redirects=False)
        if response.status_code == 200:
            return json.loads(response.text)
        return False

    @staticmethod
    def migrate(data, base_url):
        headers = {
            'Authorization': 'Bearer ' + data['access_token'],
            'Content-Type': 'application/json'
        }
        fabel_id = data['fabel_id']
        url = urljoin(base_url, f'/v2/users/{fabel_id}/migrations')
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
    def get_balance(fabel_id, access_token, base_url):
        url = urljoin(base_url, f'/v2/users/{fabel_id}/balances')
        headers = create_headers(access_token)
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)
        balances = json.loads(response.text)['balances']
        return balances[0] if balances else {}

    @staticmethod
    def charge(data, access_token, base_url) -> Result:
        url = urljoin(base_url, '/v2/charges')
        headers = create_headers(access_token)

        response = requests.post(url, headers=headers, data=json.dumps(data), verify=True, allow_redirects=False)

        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            return Result(is_success=True, error=None)

        if response.status_code == status.HTTP_403_FORBIDDEN:
            return Result(is_success=False, error=response.json()['error_description'])

        # need to introduce global error handling
        raise Exception('Error selecting a book.', response.text)

    @staticmethod
    def borrowed_releases(access_token, base_url):
        url = urljoin(base_url, '/v2/releases/groups/borrowed/releases')
        headers = create_headers(access_token)

        get_response = requests.get(url, headers=headers, verify=True, allow_redirects=False)

        releases = [release.get('id') for release in get_response.json()['releases']]
        return releases


class Coupon:

    @staticmethod
    def redeem(fabel_id, access_token, coupon, base_url):
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        data = json.dumps({'coupon': coupon})
        url = urljoin(base_url, f'/v2/users/{fabel_id}/coupons/redemptions')
        response = requests.post(url, data=data, headers=headers, verify=True, allow_redirects=False)
        return response.status_code


class Payment:

    @staticmethod
    def stripe_setup_intents(access_token, base_url):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
        }
        url = urljoin(base_url, '/v2/billing/setupintents')
        data = {
            'payment_type': 3
        }
        data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return json.loads(response.text)
        return False

    @staticmethod
    def stripe_payment_methode(access_token, reference, base_url):
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
        }
        url = urljoin(base_url, '/v2/billing/paymentmethods')
        data = {
            'payment_type': 3,
            'reference': reference
        }
        data = json.dumps(data)
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return json.loads(response.text)
        return False


class BEATAPI():

    @staticmethod
    def get_most_listen_to(access_token, base_url) -> Dict:
        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/json',
        }
        url = urljoin(base_url, '/v2/releases/groups/1')
        response = requests.get(url, headers=headers, verify=True, allow_redirects=False)

        if response.status_code == 200:
            response = json.loads(response.text)
            return response
        else:
            raise Exception(f'Failed to get list of books: status code {response.status_code}')

    @staticmethod
    def validate_file(xml, base_url):
        url = urljoin(base_url, 'https://ds.beat.delivery/v1/sources/onix')
        headers = {
            "Content-Type": "multipart/form-data, boundary=1000"
        }
        response = requests.post(url, data=xml, headers=headers)
        return response.text
