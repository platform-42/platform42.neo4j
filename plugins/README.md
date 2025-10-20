# Collections Plugins Directory

This directory can be used to ship various plugins inside an Ansible collection. Each plugin is placed in a folder that
is named after the type of plugin it is in. It can also include the `module_utils` and `modules` directory that
would contain module utils and modules respectively.

Here is an example directory of the majority of plugins currently supported by Ansible:

```
└── plugins
    ├── action
    ├── become
    ├── cache
    ├── callback
    ├── cliconf
    ├── connection
    ├── filter
    ├── httpapi
    ├── inventory
    ├── lookup
    ├── module_utils
    ├── modules
    ├── netconf
    ├── shell
    ├── strategy
    ├── terminal
    ├── test
    └── vars
```




Json Schema met regexp voor Graoh
{
  "type": "object",
  "properties": {
    "label": { "type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$" },
    "relation_type": { "type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$" },
    "entity_name": { "type": "string", "pattern": "^[A-Za-z_][A-Za-z0-9_]*$" },
    "properties": {
      "type": "object",
      "patternProperties": {
        "^[A-Za-z_][A-Za-z0-9_]*$": { "type": ["string","number","boolean","null"] }
      },
      "additionalProperties": false
    }
  },
  "required": ["label"]
}

## scopes
* `label`	used in query text	regex (^[A-Za-z_][A-Za-z0-9_]*$)
* `relation_type`	used in query text	same regex
* `entity_name`	often part of a MERGE or MATCH key	same regex
* `property keys`	appear in SET clauses	same regex for keys only
* `property values`	don’t validate here (they’re parameterized later)	leave to runtime


An exception occurred during task execution. To see the full traceback, use -vvv. The error was: TypeError: cypher_edge_add() got an unexpected keyword argument 'relation_type'
fatal: [localhost]: FAILED! => {"changed": false, "module_stderr": "Traceback (most recent call last):\n  
File \"/Users/diederickdebuck/.ansible/tmp/ansible-tmp-1760704594.453333-10272-168001985162247/AnsiballZ_edge.py\", line 107, in <module>\n
    _ansiballz_main()\n
      File \"/Users/diederickdebuck/.ansible/tmp/ansible-tmp-1760704594.453333-10272-168001985162247/AnsiballZ_edge.py\", line 99, in _ansiballz_main\n    invoke_module(zipped_mod, temp_path, ANSIBALLZ_PARAMS)\n
      File \"/Users/diederickdebuck/.ansible/tmp/ansible-tmp-1760704594.453333-10272-168001985162247/AnsiballZ_edge.py\", line 47, in invoke_module\n    runpy.run_module(mod_name='ansible_collections.platform42.neo4j.plugins.modules.edge', init_globals=dict(_module_fqn='ansible_collections.platform42.neo4j.plugins.modules.edge', _modlib_path=modlib_path),\n
        File \"/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/runpy.py\", line 224, in run_module\n
          return _run_module_code(code, init_globals, run_name, mod_spec)
            File \"/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/runpy.py\", line 96, in _run_module_code\n
                _run_code(code, mod_globals, init_globals,\n
                  File \"/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/runpy.py\", line 86, in _run_code\n    exec(code, run_globals)\n  
                  File \"/var/folders/z5/1pb7vv7j5rl70ghkj4_flf9h0000gn/T/ansible_platform42.neo4j.edge_payload_n57obq6t/ansible_platform42.neo4j.edge_payload.zip/ansible_collections/platform42/neo4j/plugins/modules/edge.py\", line 204, in <module>\n
                    File \"/var/folders/z5/1pb7vv7j5rl70ghkj4_flf9h0000gn/T/ansible_platform42.neo4j.edge_payload_n57obq6t/ansible_platform42.neo4j.edge_payload.zip/ansible_collections/platform42/neo4j/plugins/modules/edge.py\", line 181, in main\n
                    File \"/var/folders/z5/1pb7vv7j5rl70ghkj4_flf9h0000gn/T/ansible_platform42.neo4j.edge_payload_n57obq6t/ansible_platform42.neo4j.edge_payload.zip/ansible_collections/platform42/neo4j/plugins/modules/edge.py\", line 88, in edge\n
                    File \"/var/folders/z5/1pb7vv7j5rl70ghkj4_flf9h0000gn/T/ansible_platform42.neo4j.edge_payload_n57obq6t/ansible_platform42.neo4j.edge_payload.zip/ansible_collections/platform42/neo4j/plugins/module_utils/cypher.py\", line  , in edge_add\n
                    TypeError: cypher_edge_add() got an unexpected keyword argument 'relation_type'\n", "module_stdout": "", "msg": "MODULE FAILURE: No start of json char found\nSee stdout/stderr for the exact error", "rc": 1}

