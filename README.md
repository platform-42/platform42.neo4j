# platform42.neo4j

Ansible collection for managing **Neo4j graph databases**: create and update vertices (nodes), edges (relationships), execute queries, and clean up the database. This collection provides a declarative, idempotent interface to Neo4j, allowing automation of graph data management in a consistent and reliable way.

---

## Features

- **Vertex management (`vertex` module)**  
  Create or update nodes in the graph with specified labels and properties. Supports idempotent operations using Cypher `MERGE`.

- **Edge management (`edge` module)**  
  Create relationships between vertices with configurable direction, type, and properties. Also uses `MERGE` for idempotent updates.

- **Query execution (`query_read` and `query_write` modules)**  
  Run read-only or write Cypher queries against the graph. Supports parameterized queries and returns JSON-serializable results including summary statistics.

- **Database cleanup (`cleanup` or custom cleanup scripts)**  
  Easily remove nodes, relationships, or entire datasets by executing Cypher commands in an automated, repeatable manner.

- **Statistics and diagnostics**  
  Each module returns detailed execution summaries (nodes/relationships created, deleted, properties set, etc.), enabling auditability and observability in automation pipelines.

---

## Installation

```bash
# Install Python Neo4j driver
pip3 install neo4j
pip3 install regex

# Install collection from Ansible Galaxy
ansible-galaxy collection install platform42.neo4j
```

The last step is not mandatory. 
It is to provide ansible-doc access to the document pages.
The playbooks that utilise this collection, always install it before usage.