import logging

from neo4j import GraphDatabase


class Neo4JClient:

    def __init__(self, host="bolt://localhost:7687", username="neo4j", password="123456"):
        self.driver = GraphDatabase.driver(host, auth=(username, password))
        self.log = logging.getLogger(__name__)

    def find_namespace(self, ns_str):
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

    def create_syntax(self, syntax, regex, ns):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_and_return_syntax, syntax, regex, ns)
            if result:
                self.log.debug("Syntax creation was successful")
            else:
                self.log.debug("Syntax creation failed")

    @staticmethod
    def _create_and_return_syntax(tx, syntax, regex, ns):
        query = (
            "MATCH (ns:Namespace) WHERE ns.mrnNamespace = $ns "
            "CREATE (s:NamespaceSyntax {abnfSyntax: $syntax, regex: $regex}) "
            "CREATE (s)-[:DESCRIBES]->(ns) "
            "RETURN s"
        )
        result = tx.run(query, ns=ns, syntax=syntax, regex=regex)
        result = [row["s"] for row in result]
        if result:
            return result[0]
        return None

    def close(self):
        self.log.info("Closing Neo4J client")
        self.driver.close()
