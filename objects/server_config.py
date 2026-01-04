class ServerConfig:
    def __init__(self, serverID: str, postingChannelID: str, active: bool):
        self.serverID: str = serverID
        self.postingChannelID: str = postingChannelID
        self.active: bool = active

    @staticmethod
    def fromDict(data: dict):
        return ServerConfig(
            serverID = data.get("serverID", ""),
            postingChannelID = data.get("postingChannelID", ""),
            active = data.get("active", False)
        )
    
    def toDict(self) -> dict:
        return {
            "serverID": self.serverID,
            "postingChannelID": self.postingChannelID,
            "active": self.active
        }