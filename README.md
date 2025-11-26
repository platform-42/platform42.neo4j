# platform42.neo4j - release 4.2.0

Ansible collection for managing **Neo4j graph databases**: create and update vertices (nodes), edges (relationships), constraints, execute queries, and clean up the database. This collection provides a declarative, idempotent interface to Neo4j, allowing automation of graph data management in a consistent and reliable way.

## release 4.3.0 notes
- implemented `platform.neo4j.edge_bulk` primitve
- implemented support for empty `set_clause` and `set_relation_predicate`
- added Cyher templates for `VERTEX_BULK_ADD`, `VERTEX_BULK_ADD_SINGLETON`, `EDGE_BULK_ADD` and `EDGE_BULK_ADD_BI`
- new Cypher templates return a dummy value and are not terminated by a semi-colon
- implemented responsetime measurements for bulk primitves

## release 4.2.0 notes
- function results are now returend as tuples consisting: result, payload and diagnostics
- implemented `platform.neo4j.vertex_bulk` primitve
- splitted `argument_spec` into 3 parts:
  `argument_spec_neo4j` -> connection spec
  `argument_spec_xxx` -> spec related to neo4j primitives
  `argument_spec_xxx_bulk` -> additional spec related for bulk processing (input-file)
- dedupped input validations

## release 4.1.0 notes
- renamed `platform42.neo4j.query_read` to `platform.neo4j.query`
- added typecasting for query `parameters`
- added `write_access` parameter for `platform42.neo4j.query_read`. Default `False`, which implies: non distructive readonly queries on graph database

---

## special behavior 

A relationship is defined as a path between 2 nodes (n)-[r]->(n).
In most cases, merging identical relationships makes sense.
With moneylaundering concepts, a TRANSACTION is a relationship that mandates "duplicates". 
For those cases, a relationship property can be designated as the defining unique key. 

Consider this edge definition (relationship):
```yaml
- name: "create TRANSACTION relationship"
  platform42.neo4j.edge:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    type: TRANSACTION
    from:
      label: Account
      entity_name: IBAN_1
    to:
      label: Account
      entity_name: IBAN_2
    properties:
      amount: 
        value: 1000
        type: float
      transaction_date: 
        value: 2025-10-31T15:00:00.000
        type: datetime
    state: PRESENT
    unique_key: transction_date
  register: transaction
```

`amount` and `transaction_date` are properties of `TRANSACTION` relationship.
If `transaction_date` is designated as `unique_key`, it will internally create an edge with `transaction_date` as a unique identifier.

```text
MATCH (a:`Account` {entity_name: "IBAN_1"})
MATCH (b:`Account` {entity_name: "IBAN_2"})
MERGE (a)-[r:`TRANSACTION` {transction_date: "2025-10-31T15:00:00.000" }]->(b)
```

---

## Features

- **Vertex management (`vertex` and `vertex_bulk` module)**  
  Create or update nodes in the graph with specified labels and properties. Supports idempotent operations using Cypher `MERGE`.

- **Edge management (`edge` and `vertex_bulk` module)**  
  Create relationships between vertices with configurable direction, type, and properties. Also uses `MERGE` for idempotent updates.

- **Query execution (`query` module)**  
  Run read-only or write Cypher queries against the graph. Supports parameterized queries and returns JSON-serializable results including summary statistics.

- **Database cleanup (`graph_reset`)**  
  Easily remove nodes, relationships, or entire datasets by executing Cypher commands in an automated, repeatable manner.

- **Constraint management (`constraint` module)**
  Define and enforce schema-level rules in the Neo4j database. Supports creating unique property constraints on nodes using Cypher CREATE CONSTRAINT … IF NOT EXISTS, ensuring data integrity and idempotent schema management.

- **Label management (`label` module)**
  Manage labels on existing Neo4j nodes declaratively through Ansible. This module allows you to add or remove labels on nodes, supporting idempotent operations via Cypher SET n:Label and REMOVE n:Label.

- **Statistics and diagnostics**  
  Each module returns detailed execution summaries (nodes/relationships created, deleted, properties set, etc.), enabling auditability and observability in automation pipelines.

---

## Installation

```bash
# Install Python Neo4j driver
pip3 install neo4j
pip3 install regex

# Install collection from Ansible Galaxy
ansible-galaxy collection install git@github.com:platform-42/platform42.neo4j.git
```

For usage from Ansible playbooks, please download our sample U-bahn project
`git@github.com:platform-42/ansbl-play-u_bahn-sample.git`

---

## Usage

Ansible Neo4j collection can be used for both Cloud and localhost setups.
Only NEO4J_URI connection string is different.

```yaml

# vars/settings/cloud/settings.yml (AURA)
---
AURA_INSTANCEID: 123456789ABC
NEO4J_URI: "neo4j+s://{{ AURA_INSTANCEID }}.databases.neo4j.io"
NEO4J_USERNAME: neo4j
NEO4J_PASSWORD: ************
NEO4J_DATABASE: <project>|defaults to neo4j

# vars/settings/local/settings.yml (localhost)
---
NEO4J_URI: neo4j://127.0.0.1:7687
NEO4J_USERNAME: neo4j
NEO4J_PASSWORD: ************
NEO4J_DATABASE: <project>|defaults to neo4j

# cleanup graph
- name: "cleanup Graph database"
  platform42.neo4j.graph_reset:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
  register: datahase

# create node
#   - unique determines whether duplicates should be seen as 1 or not, default: TRUE
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

# create relationship between 2 nodes
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
      distance: 
        value: 1.2
        type: float
      line: 
        value: "U2"
        type: str
    bi_directional: True
    state: PRESENT
  register: track

# put unique constraint on property
- name: "Put unique constraint on entity_name of Account vertex"
  platform42.neo4j.constraint:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    label: Account
    property: entity_name
    state: PRESENT
  register: entity_name

# put additional label Suspect on existing node with label Account
- name: "create Suspect label on Account:A4"
  platform42.neo4j.label:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    base_label: Account
    entity_name: A4
    label: Suspect
    state: PRESENT
  register: suspect

#
# every module has identical response structure
# registered variable consists of:
#
#   var-name.
#     module-name.
#       cypher_query        -> cypher query with bindings (no values)
#       cypher_params       -> cypher values for bindings
#       cypher_query_inline -> cypher query with values (for debugging)
#       cypher_response     -> answer from Neo4j
#       stats               -> impact of the module on Neo4j
#
#   e.g.:
#    ----------------------------------------------
#     <register>  . <module-name> . <field>
#    ----------------------------------------------
#     station     . vertex        . cypher_query
#     track       . edge          . cypher_query
#     entity_name . constraint    . stats
#     suspect     . label         . cypher_response
#    ----------------------------------------------

```

---

## Neo4j properties (and parameters)

Neo4j properties are additional attributes that can be stored with a vertex or edge 
By default, Ansible translate all properties to string data type resulting in loss of type conext.

```yaml
# 
#   Consider this input YAML:
#     Internally, in amount is considered as a string
#     since our module needs to be abstract, we need to provide extra 
#     type information to cast the value correctly, without hardcoding it
#
properties:
  amount: 1200
  timestamp: "2025-10-02T09:00:00Z"
```

As a consequence a property must implement both `type` and `value`
`type` can be `str|int|float|bool|datetime`. More complex types are not supported (yet)

```yaml
#
#   By splitting a property into a value and type, we can
#   provide a safe type cast inside the edge and vertex modules
#
properties:
  amount:
    value: 1200
    type: int
  timestamp:
    value: "2025-10-02T09:00:00Z"
    type: datetime

#
# cypher query example 
#   - usage of bindings to transfer values to query $entity_name = parameters.entity_name
#   - typed parameters: casted value = type(value)
#   - write_access: True -> query will update graph
#
- name: "initial value for Cell:{{ item.entity_name }}"
  platform42.neo4j.query:
    neo4j_uri: "{{ NEO4J_URI }}"
    database: "{{ NEO4J_DATABASE }}"
    username: "{{ NEO4J_USERNAME }}"
    password: "{{ NEO4J_PASSWORD }}"
    query: |
      MATCH (c:Cell {entity_name: $entity_name})
      SET c.color = $color, c.domain = [$color]
      WITH c, $color AS color
      MATCH (c)-[:SEES]->(n:Cell)
      WHERE n.color = 0
      SET n.domain = [x IN n.domain WHERE x <> color]
      RETURN c, n
    write_access: True
    parameters:
      entity_name: 
        value: "{{ item.entity_name }}"
        type: str
      color: 
        value:  "{{ item.color }}"
        type: int
```

