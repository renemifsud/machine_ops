import requests, json


class AppController:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        url = self.base_url + "/get-auth-token/60"
        auth = requests.auth.HTTPBasicAuth(username, password)
        response = self.send_request("GET", url, auth=auth)
        if response:
            self.token = response["token"]

    def get_solutions(self, identifier=None, params=None):
        if identifier:
            url = self.base_url + "/solutions" + "/" + identifier
        else:
            url = self.base_url + "/solutions"
        try:
            if not params:
                results = self.send_request("GET", url=url)
            else:
                results = self.send_request("GET", url=url, params=params)
        except Exception as err:
            print(err)
            return None
        else:
            return results

    def create_solutions(self, data):
        url = self.base_url + "/solutions"
        try:
            self.send_request("POST", url=url, data=data)
        except Exception as err:
            print(err)

    def get_playbooks(self, identifier=None, params=None):
        if identifier:
            url = self.base_url + "/playbooks" + "/" + identifier
        else:
            url = self.base_url + "/playbooks"
        try:
            if not params:
                results = self.send_request("GET", url=url)
            else:
                results = self.send_request("GET", url=url, params=params)
        except Exception as err:
            print(err)
            return None
        else:
            return results

    def create_playbooks(self, data):
        url = self.base_url + "/playbooks"
        try:
            self.send_request("POST", url=url, data=data)
        except Exception as err:
            print(err)

    def send_request(self, method, url, data=None, auth=None, params=None):
        headers = {"Content-Type": "application/json"}
        data = json.dumps(data)

        if not auth:
            auth = requests.auth.HTTPBasicAuth(self.token, "")

        if "get" in method.lower():
            if not params:
                response = requests.get(url=url, headers=headers, auth=auth)
            else:
                response = requests.get(
                    url=url, headers=headers, auth=auth, params=params
                )
        elif "put" in method.lower():
            response = requests.put(url=url, headers=headers, data=data, auth=auth)
        elif "post" in method.lower():

            response = requests.post(url=url, headers=headers, data=data, auth=auth)

        content = response.json()

        if int(response.status_code) >= 200 and int(response.status_code) <= 399:
            return content
        elif int(response.status_code) == 401:
            self.token = None
        else:
            raise Exception(
                f"Error sending requests [{response.status_code}] with error message [{content}]"
            )
