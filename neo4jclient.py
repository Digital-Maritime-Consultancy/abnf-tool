#  Copyright 2022 International Association of Marine Aids to Navigation and Lighthouse Authorities
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging

from neo4j import GraphDatabase


class Neo4JClient:

    def __init__(self, host="bolt://localhost:7687", username="neo4j", password="123456"):
        self.driver = GraphDatabase.driver(host, auth=(username, password))
        self.log = logging.getLogger(__name__)

    def find_namespace(self, ns_str: str):
        with self.driver.session() as session:
            return session.read_transaction(self._find_and_return_namespace, ns_str)

    @staticmethod
    def _find_and_return_namespace(tx, ns_str):
        query = (
            "MATCH (ns:Namespace) "
            "WHERE ns.mrnNamespace = $ns_str "
            "RETURN ns"
        )
        result = tx.run(query, ns_str=ns_str)
        result = [row["ns"] for row in result]
        if result:
            return result[0]
        return None

    def create_syntax(self, syntax, regex, ns, ns_owner: dict):
        with self.driver.session() as session:
            namespace = session.read_transaction(self._find_and_return_namespace, ns)
            if not namespace:
                self.create_namespace(ns)
            result = session.write_transaction(self._create_and_return_syntax, syntax, regex, ns, ns_owner)
            if result:
                self.log.info("Syntax creation was successful")
                return True
        self.log.error("Syntax creation failed")
        return False

    @staticmethod
    def _create_and_return_syntax(tx, syntax, regex, ns, ns_owner):
        query = (
            "MATCH (ns:Namespace) WHERE ns.mrnNamespace = $ns "
            "CREATE (s:NamespaceSyntax {abnfSyntax: $syntax, regex: $regex, mrnNamespace: $ns}) "
            "CREATE (no:Owner $ns_owner) "
            "CREATE (s)-[:DESCRIBES]->(ns) "
            "CREATE (no)-[:OWNS_NAMESPACE]->(s) "
            "RETURN s"
        )
        result = tx.run(query, ns=ns, syntax=syntax, regex=regex, ns_owner=ns_owner)
        result = [row["s"] for row in result]
        if result and len(result) > 0:
            return result[0]
        return None

    def create_namespace(self, ns: str):
        parent_namespace = None
        if ns and ':' in ns:
            parent_namespace = ns[:ns.rindex(':')]
            parent_ns = self.find_namespace(parent_namespace)
            if not parent_ns:
                self.create_namespace(parent_namespace)
        with self.driver.session() as session:
            return session.write_transaction(self._create_and_return_namespace, ns, parent_namespace)

    @staticmethod
    def _create_and_return_namespace(tx, ns: str, parent_ns: str = None):
        if parent_ns:
            query = (
                "MATCH (n1:Namespace) WHERE n1.mrnNamespace = $ns1 "
                "CREATE (n2:Namespace {mrnNamespace: $ns2}) "
                "CREATE (n2)-[:EXTENDS]->(n1) "
                "RETURN n2"
            )
        else:
            query = (
                "CREATE (n2:Namespace {mrnNamespace: $ns2}) "
                "RETURN n2"
            )
        result = tx.run(query, ns1=parent_ns, ns2=ns)
        result = [row["n2"] for row in result]
        if result:
            return result[0]
        return None

    def close(self):
        self.log.info("Closing Neo4J client")
        self.driver.close()
