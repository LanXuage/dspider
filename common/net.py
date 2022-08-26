#!/bin/env python3

import base64
import hashlib
from common.helpers import preprocess_dict, preprocess_url


class Request:
    def __init__(self, url : str, method='GET', headers=None, payload=None) -> None:
        self.url = preprocess_url(url)
        if not method:
            method = 'GET'
        self.method = method
        if not headers:
            headers = dict()
        self.headers = headers
        if not payload:
            payload = b''
        if isinstance(payload, str):
            payload = payload.encode()
        self.payload = payload
    
    def get_req_hash(self):
        data = preprocess_url(self.url) + ':' + self.method + ':' + preprocess_dict(self.headers) + ':' + base64.b64encode(self.payload).decode()
        return hashlib.md5(data.encode()).hexdigest()

class Response:
    def __init__(self, url : str, headers, response_raw : bytes) -> None:
        self.url = url
        self.raw = response_raw
        self.headers = headers