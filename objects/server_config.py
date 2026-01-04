class ServerConfig:
    def __init__(self, serverID: str, channelID: str, enabled: bool):
        self.serverID: str = serverID
        self.channelID: str = channelID
        self.enabled: bool = enabled

    @staticmethod
    def fromDict(data: dict):
        return ServerConfig(
            serverID = data.get("serverID", ""),
            channelID = data.get("channelID", ""),
            enabled = data.get("enabled", False)
        )
    
    def toDict(self) -> dict:
        return {
            "serverID": self.serverID,
            "channelID": self.channelID,
            "enabled": self.enabled
        }