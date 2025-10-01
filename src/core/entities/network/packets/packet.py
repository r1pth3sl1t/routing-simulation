class TransportLayerPacket:
    def __init__(self, src_router_id, dest_router_id, message_size):
        self.src_router_id = src_router_id
        self.dest_router_id = dest_router_id
        self.message_size = message_size
        pass

    def get_header_size(self):
        pass

    def get_message_size(self):
        return self.message_size + self.get_header_size()