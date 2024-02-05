#!/usr/bin/env python
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


import collections
import json
import os
import tempfile
from pathlib import Path

import black
from click.testing import CliRunner
from jinja2 import Environment, FileSystemLoader

code_root = Path(__file__).absolute().parent.parent
asciidocs_dir = code_root / "docs/examples"
flight_recorder_dir = code_root.parent / "clients-flight-recorder"
report_path = flight_recorder_dir / "recordings/docs/parsed-alternative-report.json"
substitutions = {"type": "doc_type", "from": "from_"}

jinja_env = Environment(
    loader=FileSystemLoader([code_root / "utils" / "templates"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

files_to_generate = [
    "/search/search.asciidoc",
    "aggregations/bucket/datehistogram-aggregation.asciidoc",
    "aggregations/bucket/filter-aggregation.asciidoc",
    "aggregations/bucket/terms-aggregation.asciidoc",
    "aggregations/metrics/valuecount-aggregation.asciidoc",
    "api-conventions.asciidoc",
    "cat/indices.asciidoc",
    "cluster/health.asciidoc",
    "docs/bulk.asciidoc",
    "docs/delete-by-query.asciidoc",
    "docs/delete.asciidoc",
    "docs/get.asciidoc",
    "docs/index_.asciidoc",
    "docs/reindex.asciidoc",
    "docs/update-by-query.asciidoc",
    "docs/update.asciidoc",
    "getting-started.asciidoc",
    "getting-started.asciidoc",
    "indices/aliases.asciidoc",
    "indices/create-index.asciidoc",
    "indices/delete-index.asciidoc",
    "indices/get-index.asciidoc",
    "indices/get-mapping.asciidoc",
    "indices/put-mapping.asciidoc",
    "indices/templates.asciidoc",
    "indices/update-settings.asciidoc",
    "mapping.asciidoc",
    "mapping/fields/id-field.asciidoc",
    "mapping/params/fielddata.asciidoc",
    "mapping/params/format.asciidoc",
    "mapping/params/multi-fields.asciidoc",
    "mapping/types/array.asciidoc",
    "mapping/types/date.asciidoc",
    "mapping/types/keyword.asciidoc",
    "mapping/types/nested.asciidoc",
    "mapping/types/numeric.asciidoc",
    "query-dsl.asciidoc",
    "query-dsl/bool-query.asciidoc",
    "query-dsl/exists-query.asciidoc",
    "query-dsl/function-score-query.asciidoc",
    "query-dsl/match-all-query.asciidoc",
    "query-dsl/match-phrase-query.asciidoc",
    "query-dsl/match-query.asciidoc",
    "query-dsl/multi-match-query.asciidoc",
    "query-dsl/nested-query.asciidoc",
    "query-dsl/query-string-query.asciidoc",
    "query-dsl/query_filter_context.asciidoc",
    "query-dsl/range-query.asciidoc",
    "query-dsl/regexp-query.asciidoc",
    "query-dsl/term-query.asciidoc",
    "query-dsl/terms-query.asciidoc",
    "query-dsl/wildcard-query.asciidoc",
    "search.asciidoc",
    "search/count.asciidoc",
    "search/request-body.asciidoc",
    "search/request/from-size.asciidoc",
    "search/request/scroll.asciidoc",
    "search/request/sort.asciidoc",
    "search/suggesters.asciidoc",
    "setup/install/check-running.asciidoc",
    "setup/logging-config.asciidoc",
]


ParsedSource = collections.namedtuple("ParsedSource", ["api", "params", "body"])


def blacken(filename):
    runner = CliRunner()
    result = runner.invoke(
        black.main, [str(filename), "--line-length=75", "--target-version=py37"]
    )
    assert result.exit_code == 0, result.output


def main():
    for filepath in asciidocs_dir.iterdir():
        if filepath.name.endswith(".asciidoc"):
            filepath.unlink()

    if not flight_recorder_dir.exists() or not report_path.exists():
        raise RuntimeError(
            f"clients-flight-recorder repository not checked out at {flight_recorder_dir}"
        )

    with report_path.open() as f:
        report = json.loads(f.read())

    t = jinja_env.get_template("example")

    for exm in report:
        if exm["lang"] != "console":
            continue
        if exm["source_location"]["file"] not in files_to_generate:
            continue

        parsed_sources = []
        for src in exm["parsed_source"]:
            params = (src.get("params") or {}).copy()
            params.update(src.get("query") or {})
            params = {
                k: (list(v.split(",")) if isinstance(v, str) and "," in v else v)
                for k, v in params.items()
            }

            parsed_sources.append(
                ParsedSource(
                    api=src["api"],
                    params={
                        substitutions.get(k, k): repr(v) for k, v in params.items()
                    },
                    body=src.get("body", None) or None,
                )
            )

        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp_file:
            tmp_file.write(t.render(parsed_sources=parsed_sources))

        blacken(tmp_file.name)

        with open(tmp_file.name) as f:
            data = f.read()
            data = data.rstrip().replace(",)", ")")

        os.unlink(tmp_file.name)

        with (asciidocs_dir / f"{exm['digest']}.asciidoc").open(mode="w") as f:
            f.truncate()
            f.write(
                f"""// {exm['source_location']['file']}:{exm['source_location']['line']}

[source, python]
----
{data}
----"""
            )


if __name__ == "__main__":
    main()
