# platform42.neo4j

Ansible collection for managing **Neo4j graph databases**: create and update vertices (nodes), edges (relationships), execute queries, and clean up the database. This collection provides a declarative, idempotent interface to Neo4j, allowing automation of graph data management in a consistent and reliable way.

---

## To Do

Properties are provided as an Dict. 
By default, Ansible translate all properties to string. 
Therefore we lose type context.
So amount, distance, timestamp formats will be currently treated as a string which is incorrect if you want to perform calculations.

```yaml
# 
#   Consider this input YAML:
#     Internally, in a Ansible Module, amount is considered as a string
#     since our module needs to be abstract, we need to provide extra 
#     type information to cast the value correctly, without hardcoding it
#
properties:
  amount: 1200
  timestamp: "2025-10-02T09:00:00Z"

#
#   By splitting the property into a value and type, we can
#   provide a safe and correct cast inside the edge and vertex modules
#   for properties
#
properties:
  amount:
    value: 1200
    type: int
  timestamp:
    value: "2025-10-02T09:00:00Z"
    type: datetime
```

---

## Features

- **Vertex management (`vertex` module)**  
  Create or update nodes in the graph with specified labels and properties. Supports idempotent operations using Cypher `MERGE`.

- **Edge management (`edge` module)**  
  Create relationships between vertices with configurable direction, type, and properties. Also uses `MERGE` for idempotent updates.

- **Query execution (`query_read` and `query_write` modules)**  
  Run read-only or write Cypher queries against the graph. Supports parameterized queries and returns JSON-serializable results including summary statistics.

- **Database cleanup (`graph_reset` or custom cleanup scripts)**  
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

Ansible Neo4j collection can be used for both Cloud and localhost setups.
Only NEO4J_URI connection string is different.

```yaml

# vars/settings/cloud/settings.yml
#   use if Neo4j is used in cloud setup (AURA)
---
AURA_INSTANCEID: 123456789ABC
NEO4J_URI: "neo4j+s://{{ AURA_INSTANCEID }}.databases.neo4j.io"
NEO4J_USERNAME: neo4j
NEO4J_PASSWORD: ************
NEO4J_DATABASE: neo4j

# vars/settings/local/settings.yml
#   use if Neo4j is used in localhost setup 
---
NEO4J_URI: neo4j://127.0.0.1:7687
NEO4J_USERNAME: neo4j
NEO4J_PASSWORD: ************
NEO4J_DATABASE: ubahn # I gave its own name in localhost setup

# cleanup graph
- name: "cleanup Graph database"
  platform42.neo4j.graph_reset:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
  register: graph
#
# interesting variables to inspect
#   <graph>.<graph_reset>.<item>
#     graph.graph_reset.cypher_response
#     graph.graph_reset.cypher_query_inline
#

# create node
- name: "create station Station:Pankow"
  platform42.neo4j.vertex:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    label: Station
    entity_name: "Pankow"
    state: PRESENT
  register: station
#
# interesting variables to inspect
#   <station>.<vertex>.<item>
#     station.vertex.cypher_response
#     station.vertex.cypher_query_inline
#

# create relationship
- name: "create U2 TRACK:Pankow - Vinetastraße"
  platform42.neo4j.edge:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    type: TRACK
    from:
      label: Station
      entity_name: "Pankow"
    to:
      label: Station
      entity_name: "Vinetastraße"
    properties:
      distance: 1.2
      line: "U2"
    bi_directional: True
    state: PRESENT
  register: track
#
# interesting variables to inspect
#   <track>.<edge>.<item>
#     track.edge.cypher_response
#     track.edge.cypher_query_inline
#
```