#!/bin/bash
#
# Copyright 2022 International Association of Marine Aids to Navigation and Lighthouse Authorities
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
set -eou pipefail
MODE="$1"

ARGS=()

if [[ -v REDIS_HOST ]]; then
  ARGS+=("--redis_host" "$REDIS_HOST")
fi

if [[ -v REDIS_PORT ]]; then
  ARGS+=("--redis_port" "$REDIS_PORT")
fi

if [[ -v REDIS_DB ]]; then
  ARGS+=("--redis_db" "$REDIS_DB")
fi

if [[ -v REDIS_PASSWORD ]]; then
  ARGS+=("--redis_password" "$REDIS_PASSWORD")
fi

if [[ -v NEO4J_URI ]]; then
  ARGS+=("--neo4j_uri" "$NEO4J_URI")
fi

if [[ -v NEO4J_USER ]]; then
  ARGS+=("--neo4j_user" "$NEO4J_USER")
fi

if [[ -v NEO4J_PASSWORD ]]; then
  ARGS+=("--neo4j_password" "$NEO4J_PASSWORD")
fi

if [[ $MODE == "server" ]]; then
  if [[ ${#ARGS[@]} -eq 0 ]]; then
    exec python3 server.py
  else
    exec python3 server.py "${ARGS[@]}"
  fi
elif [[ $MODE == "bootstrap" ]]; then
  if [[ ${#ARGS[@]} -eq 0 ]]; then
    exec python3 abnf-tool.py
  else
    exec python3 -u abnf-tool.py "${ARGS[@]}"
  fi
else
  exec "$@"
fi
exit $?
