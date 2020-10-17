#!/usr/bin/env python
"""Helper functions to authenticate with FMC and send basic CRUD requests.

Copyright (c) 2018-2019 Cisco and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning


# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Helper Functions
class fmc_requests():
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.fmc_authenticate(self.host, self.username, self.password)

    def fmc_authenticate(self, host, username, password):
        """Authenticate with FMC; get and store the auth token and domain UUID."""
        print("\n==> Authenticating with FMC and requesting an access token")

        self.headers = {}
        self.authentication = HTTPBasicAuth(username, password)

        response = requests.post(
            f"https://{host}/api/fmc_platform/v1/auth/generatetoken",
            headers=self.headers,
            auth=self.authentication,
            verify=False
        )
        response.raise_for_status()

        # Get the authentication token and domain UUID from the response
        access_token = response.headers.get("X-auth-access-token")
        domain_uuid = response.headers.get("DOMAIN_UUID")

        # Update the headers used for subsequent requests to FMC
        self.headers["DOMAIN_UUID"] = domain_uuid
        self.headers["X-auth-access-token"] = access_token

        self.access_token = access_token
        self.domain_uuid = domain_uuid

    def _create_url(self, endpoint_path):
        """Create an FMC configuration API endpoint URL."""
        _url = f"https://{self.host}/api/fmc_config/v1/domain/{self.domain_uuid}/{endpoint_path}"
        return _url

    def post(self, endpoint_path, data):
        """Send a POST request to FMC and return the parsed JSON response."""
        url = self._create_url(endpoint_path)

        response = requests.post(url, headers=self.headers, json=data, verify=False)
        response.raise_for_status()

        return response.json()

    def get(self, endpoint_path):
        """Send a GET request to FMC and return the parsed JSON response."""
        url = self._create_url(endpoint_path)

        response = requests.get(url, headers=self.headers, verify=False)
        response.raise_for_status()

        return response.json()

    def delete(self, endpoint_path):
        """Send a DELETE request to FMC and return the parsed JSON response."""
        url = self._create_url(endpoint_path)

        response = requests.delete(url, headers=self.headers, verify=False)
        response.raise_for_status()

        return response.json()
