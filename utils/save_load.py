import os
import json

from utils.clogger import Clogger
from objects.server_config import ServerConfig

DATA_PATH = os.path.join("data", "servers")

class SaveLoad:
    @staticmethod
    def saveData(configs: dict, id: str):
        config = configs.get(id)
        if not config:
            Clogger.error(f"No server configuration found for server ID: {id}. Cannot save data.")
            return
        
        filepath = os.path.join(DATA_PATH, f"{id}.json")
        with open(filepath, "w") as file:
            json.dump(config.toDict(), file, indent=4)
        Clogger.info(f"Saved server configuration for server ID: {id}")

    @staticmethod
    def saveAllData(configs: dict):
        Clogger.info("Saving all server configurations...")
        for config in configs.values():
            SaveLoad.saveData(configs, config.serverID)
        Clogger.info("Finished saving all server configurations.")

    @staticmethod
    def loadData() -> dict:
        Clogger.info("Loading server configurations...")
        configs = {}

        for filename in os.listdir(DATA_PATH):
            if filename.endswith(".json"):
                filepath = os.path.join(DATA_PATH, filename)
                
                with open(filepath, "r") as file:
                    data = json.load(file)
                    serverID = data.get("serverID")
                    if serverID:
                        configs[serverID] = data
                    else:
                        Clogger.warn(f"Server config file {filename} is missing 'serverID' field.")
                        continue
                
                    config = ServerConfig.fromDict(data)
                    configs[serverID] = config
                    Clogger.info(f"Loaded server config for server ID: {serverID}")

        Clogger.info("Finished loading server configurations.")
        return configs
