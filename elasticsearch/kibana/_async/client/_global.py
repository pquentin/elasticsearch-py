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

class C:

    @_rewrite_parameters()
    async def system_status(
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
        return await self.perform_request(  # type: ignore[return-value]
            "GET",
            __path,
            params=__query,
            headers=__headers,
            endpoint_id="_global.system_status",
            path_parts=__path_parts,
        )
