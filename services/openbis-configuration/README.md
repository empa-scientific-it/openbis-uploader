# Openbis Configurator

## Introduction

This repository contains a python package which allows instance admins to quicky create test instances using a configuration file and populate them. This is more convient than clicking through various the Openbis UIs to define object types, projects and samples. This package is particularly useful in combination with a docker instance.

For the time being, the configuration is expressed in the form of a JSON file.

## Installing

To install the module, use pip as follow:

1) Checkout the package in a directory of your choosing
1) Enter the directory and type:
```
pip install .
```

Now the module is installed in your python envrionment. To avoid polluting your global python path, do consider using conda or virtual envrionments.


## Usage
### Commandline script
The main entrypoint of this module is the command line utility  `make_instance.py`. To import a configuration residing in the file `test_instance.json` use:
```
make_instance.py localhost:8443 admin changeit create ./test_instance.json
```
This assume that the instance admin for the instance on `localhost` has the username "admin" and password "changeit"

To export an existing instance to JSON, use:

```
make_instance.py localhost:8443 admin export create ./test_instance_exported.json
```


### Configuration file

The configuration file  should have the following form:

#### Data

Each space MUST have a  `code` entry and CAN contain a list of projects as a list of dictionaries. As an example:

```
spaces: [
    {"code": "SPACE1", "projects": []}
    ]
```

Each project, MUST have a `code` entry and CAN HAVE a list of collection (experiment) entries:

```
{"code": "SPACE1", "projects": [
    {"code":"PROJ1", collections:[], properties:{}}
]}
    
```
Each collection MUST have a `code` and a `type`. The type should be a defined collection type, either pre-defined in the Openbis instance or defined in a separate section of the configuration file. A collection CAN contain a list of samples (objects) and CAN contain a `properties` dictionary with collection-specific properties. These properties should be defined in the collection type definition part or using the Admin UI.

The entry looks as follows
```
{'code': 'COLL1', type:'DEFAULT_EXPERIMENT', samples: []}
```

Each sample/object in a collection has the form
```
{"type":"SAMPLE", properties: {}, code: "SAMPLE1"}
```
Each sample MUST have a `type` which is a pre-defined object type or can defined in a separate section.
Each sample CAN have a dictionary `properties` where the values of the sample properties can be specified. A sample CAN (or MUST) have a `code` if the sample codes are not generated automatically for the specific object type.

In summary, the spaces configuration for this example looks as follows:

```

    "spaces": [
        {
            "code": "SPACE1",
            "projects": [
                {
                    "code": "PROJ1",
                    "collections": [
                        {
                            "code": "COLL1",
                            "type": "DEFAULT_EXPERIMENT",
                            "samples": [
                                {"type":"SAMPLE1", "properties":{"sample_id":1}
                            ],
                            "properties": {"measurement_id": 1}
                        }
                    ]
                }
            ]
        }
    ]

```

### Master data
To define  propertis, object types, collection types and other master data, we use the follwing schema.

For property types, a list of dictionaries, one for each property
```
    "properties": [
        {
            "code": "SAMPLE_ID",
            "label": "sample_id",
            "description": "Id of sample",
            "data_type": "INTEGER"
    ]

```
For collection types a list of dictionaries of the following form
    "collection_types": [
        {
            "code":"DEFAULT_COLLECTION",
            "description":"DC",
            "properties": ["MEASUREMENT_ID"]
        }
    ],
    "object_types": [
        {
            "code": "ICP-MS-MEASUREMENT",
            "prefix": "ICPMS_MEAS",
            "properties": {"one":["SAMPLE_ID", "GAS_FLOW", "ACQ_TIMESTAMP"]}
    }
    ]
}
```

