import json
import logging
from pathlib import Path


props_default_values = {
    "String": "",
    "Password": 0,
    "Integer": 0,
    "Dropdown": "",
    "Boolean": False,
    "Textarea": "",
}

base_simulator_snapshot = {
    "entries": [
        {
            "group_id": 10513228273606543363,
            "group_instance_id": 1289083120781560139,
            "process_type": 2,
            "group_name": "Process Group Name",
            "processes": [
                {
                    "pid": 1522804,
                    "process_name": "Process Name",
                    "properties": {"CmdLine": "-m plugin_sdk.demo_app", "WorkDir": "/home/demo", "ListeningPorts": "1521"},
                }
            ],
            "properties": {"ProcessGroupVersion": "18", "Technologies": "Oracle,ORACLE_DB,DOCKER,ALL_OTHER,OTHER"},
        }
    ]
}


class PropsHandler:
    def __init__(self, log: logging.Logger):
        self.log = log

    def run(self):
        if not Path("plugin.json") in list(Path().iterdir()):
            raise Exception("psa gen-props must be run from where plugin.json is located")

        self.log.info(f"Generating properties from from {Path().absolute()}/plugin.json")
        self.generate_properties()
        self.generate_simulator_snapshot()

    def generate_properties(self):

        if Path("properties.json") in list(Path().iterdir()):
            overwrite = input("There is a properties.json file present already, overwrite? ")
            if overwrite not in ["y", "Y", "yes", "Yes"]:
                return

        new_properties = {}
        with open("plugin.json", "r") as f:
            plugin_json = json.load(f)
            props = plugin_json.get("properties", [])
            for prop in props:
                new_properties[prop["key"]] = props_default_values[prop["type"]]

        with open("properties.json", "w") as f:
            json.dump(new_properties, f, indent=2)

        self.log.info(f"Created {Path().absolute()}/properties.json")

    def generate_simulator_snapshot(self):
        with open("plugin.json", "r") as f:
            plugin_json = json.load(f)
            activation = plugin_json.get("source", {}).get("activation", "")
            if activation == "Remote":
                return

        if Path("simulator_snapshot.json") in list(Path().iterdir()):
            overwrite = input("There is a simulator_snapshot.json file present already, overwrite? ")
            if overwrite not in ["y", "Y", "yes", "Yes"]:
                return

        with open("simulator_snapshot.json", "w") as f:
            json.dump(base_simulator_snapshot, f, indent=2)
        self.log.info(f"Created {Path().absolute()}/simulator_snapshot.json")
