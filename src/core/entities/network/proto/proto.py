from src.core.entities.network.packets.data import RawData
from src.core.entities.network.packets.packet import TransportLayerPacket


class TransportLayerProtocol:
    def __init__(self, router,  message: RawData):
        self.router = router
        self.message = message
        pass

    def transmit_message(self, dest_router_id):
        pass

    def receive_message(self):
        pass
