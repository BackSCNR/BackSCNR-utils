import os
import requests


class Api:
    def __init__(
        self, base_url="https://api.backscnr.com", token_file=".token.env", timeout=5
    ):
        """
        :param base_url: The base url of the API
        :param token_file: The file to save the refresh token
        :param timeout: The timeout for requests in seconds
        """
        self.timeout = timeout
        self.base_url = base_url
        self.token_file = token_file
        self.access_token = self.get_access_token()

    def get_refresh_token(self):
        """
        Get the refresh token either from the token file if it exists
        or prompt the user to login and get the token.
        This token is used to authenticate the user.
        :return: The refresh token
        """
        if os.path.exists(self.token_file):
            # Load refresh token from file
            with open(self.token_file, "r") as f:
                refresh_token = f.read()
            print(f"Loaded saved token from {self.token_file}")
        else:
            # Prompt the user to login and get the refresh token
            print(
                "Login by going to https://backscnr.com/account/token and copying the token"
            )
            print("Then paste it here:")
            refresh_token = input("Token: ").strip()

            # Save refresh to token file
            with open(self.token_file, "w") as f:
                f.write(refresh_token)
            print(f"Saved to {self.token_file}")

        return refresh_token

    def get_access_token(self):
        """
        Returns the access token by using the refresh token.
        (1) Get refresh token from file
        (2) Use refresh token to get access token from server
        (3) Save new refresh token to file
        :return: The access token
        """
        refresh_token = self.get_refresh_token()

        # Use refresh token to get access token
        response = requests.post(
            self.base_url + "/api/token/refresh/",
            data={"refresh": refresh_token},
            timeout=5,
        )

        if response.status_code != 200:
            print("Failed to get access token using refresh token, possibly expired!")
            # Remove the token file and try again
            os.remove(self.token_file)
            return self.get_access_token()

        response_json = response.json()
        access_token = response_json["access"]
        # New refresh token generated by the server which will last longer
        new_refresh_token = response_json["refresh"]

        # Save refresh to token file
        with open(self.token_file, "w") as f:
            f.write(new_refresh_token)

        return access_token

    def get(self, url, params=None, **kwargs):
        """
        Make a GET request to the API
        :param url: The url to make the request to
        :param params: The parameters to send with the request
        :param kwargs: Additional arguments to pass to requests
        :return: The response object
        """
        response = requests.get(
            self.base_url + url,
            params=params,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=self.timeout,
            **kwargs,
        )
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"[GET] Failed {response.url} : {response.status_code} : {response.content}"
            )
        print("[GET]", response.url)
        return response

    def post(self, url, data=None, json=None, **kwargs):
        """
        Make a POST request to the API
        :param url: The url to make the request to
        :param data: The data to send with the request
        :param json: The json to send with the request
        :param kwargs: Additional arguments to pass to requests
        :return: The response object
        """
        response = requests.post(
            self.base_url + url,
            data=data,
            json=json,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=self.timeout,
            **kwargs,
        )
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"[POST] Failed {response.url} : {response.status_code} : {response.content}"
            )
        print("[POST]", response.url)
        return response
