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


## Usage
```yaml

# settings.yml
---
AURA_INSTANCEID: 123456789ABC
NEO4J_URI: neo4j+s://123456789ABC.databases.neo4j.io
NEO4J_USERNAME: neo4j
NEO4J_PASSWORD: ************
NEO4J_DATABASE: neo4j


# cleanup graph
- name: "cleanup Graph database"
  platform42.neo4j.cleanup:
    instance_id: "{{ AURA_INSTANCEID }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
  register: database

# create node
- name: "create station Station:{{ item.name }}"
  platform42.neo4j.vertex:
    instance_id: "{{ AURA_INSTANCEID }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    label: Station
    entity_name: "{{ item.name }}"
    state: PRESENT
  register: station

# create relationship
- name: "create track {{ item.line }} TRACK:{{ item.from }} - {{ item.to }}"
  platform42.neo4j.edge:
    instance_id: "{{ AURA_INSTANCEID }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    type: TRACK
    from:
      label: Station
      entity_name: "{{ item.from }}"
    to:
      label: Station
      entity_name: "{{ item.to }}"
    properties:
      distance: "{{ item.distance }}"
      line: "{{ item.line }}"
    bi_directional: True
    state: PRESENT
  register: track
```