#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.


import logging
import typing as t

from elastic_transport import ApiResponse, HttpHeaders, ObjectApiResponse, Transport
from elastic_transport.client_utils import DEFAULT, DefaultType

from elasticsearch._async.client.utils import (
    _TYPE_HOSTS,
    _base64_auth_header,
    _quote,
    _quote_query,
    _rewrite_parameters,
    client_node_configs,
)

logger = logging.getLogger("elasticsearch.kibana")


def resolve_auth_headers(
    api_key: t.Union[DefaultType, None, t.Tuple[str, str], str] = DEFAULT,
) -> HttpHeaders:
    headers = HttpHeaders()
    if api_key is not DEFAULT and api_key is not None:
        headers["authorization"] = f"ApiKey {_base64_auth_header(api_key)}"

    return headers


class Kibana:
    def __init__(
        self,
        hosts: _TYPE_HOSTS,
        *,
        api_key: t.Optional[t.Union[str, t.Tuple[str, str]]] = None,
        basic_auth: t.Optional[t.Union[str, t.Tuple[str, str]]] = None,
    ) -> None:
        node_configs = client_node_configs(hosts, cloud_id=None)
        self._headers = resolve_auth_headers(api_key=api_key)
        self.transport = Transport(node_configs)

    def __enter__(self) -> "Kibana":
        try:
            self.transport._async_call()
        except AttributeError:
            pass
        return self

    def __exit__(self, *_: t.Any) -> None:
        self.close()

    def close(self) -> None:
        """Closes the Transport and all internal connections"""
        self.transport.close()

    def perform_request(
        self,
        method: str,
        path: str,
        *,
        params: t.Optional[t.Mapping[str, t.Any]] = None,
        headers: t.Optional[t.Mapping[str, str]] = None,
        body: t.Optional[t.Any] = None,
        endpoint_id,
        path_parts,
    ) -> ApiResponse[t.Any]:
        if headers:
            request_headers = self._headers.copy()
            request_headers.update(headers)
        else:
            request_headers = self._headers

        if params:
            target = f"{path}?{_quote_query(params)}"
        else:
            target = path

        meta, resp_body = self.transport.perform_request(
            method, target, headers=request_headers, body=body
        )

        return ObjectApiResponse(body=resp_body, meta=meta)

    # AUTO-GENERATED-API-DEFINITIONS #

    @_rewrite_parameters()
    def system_status(
        self,
        *,
        v7format: t.Optional[bool] = None,
        v8format: t.Optional[bool] = None,
    ) -> ObjectApiResponse[t.Any]:
        """
        Get Kibana's current status

        :param v7format: Set to "true" to get the response in v7 format.
        :param v8format: Set to "true" to get the response in v8 format.
        """
        __path_parts: t.Dict[str, str] = {}
        __path = "/api/status"
        __query: t.Dict[str, t.Any] = {}
        if v7format is not None:
            __query["v7format"] = v7format
        if v8format is not None:
            __query["v8format"] = v8format
        __headers = {"accept": "application/json"}
        return self.perform_request(  # type: ignore[return-value]
            "GET",
            __path,
            params=__query,
            headers=__headers,
            endpoint_id="system_status",
            path_parts=__path_parts,
        )
