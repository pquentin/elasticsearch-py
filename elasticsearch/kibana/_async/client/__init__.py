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

from elastic_transport import (
    ApiResponse,
    AsyncTransport,
    HttpHeaders,
    ObjectApiResponse,
)
from elastic_transport.client_utils import DEFAULT, DefaultType

from elasticsearch._async.client.utils import (  # _quote,; _rewrite_parameters,
    _TYPE_HOSTS,
    _base64_auth_header,
    _quote_query,
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


class AsyncKibana:
    def __init__(
        self,
        hosts: _TYPE_HOSTS,
        *,
        api_key: t.Optional[t.Union[str, t.Tuple[str, str]]] = None,
        basic_auth: t.Optional[t.Union[str, t.Tuple[str, str]]] = None,
    ) -> None:
        node_configs = client_node_configs(hosts, cloud_id=None)
        self._headers = resolve_auth_headers(api_key=api_key)
        self.transport = AsyncTransport(node_configs)

    async def __aenter__(self) -> "AsyncKibana":
        try:
            await self.transport._async_call()
        except AttributeError:
            pass
        return self

    async def __aexit__(self, *_: t.Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Closes the Transport and all internal connections"""
        await self.transport.close()

    async def perform_request(
        self,
        method: str,
        path: str,
        *,
        params: t.Optional[t.Mapping[str, t.Any]] = None,
        headers: t.Optional[t.Mapping[str, str]] = None,
        body: t.Optional[t.Any] = None,
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

        meta, resp_body = await self.transport.perform_request(
            method, target, headers=request_headers, body=body
        )

        return ObjectApiResponse(body=resp_body, meta=meta)

    # AUTO-GENERATED-API-DEFINITIONS #
