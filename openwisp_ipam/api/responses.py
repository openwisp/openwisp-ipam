class HostsResponse(object):
    def __init__(self, address, used, reserved):
        self.address = address
        self.used = used
        self.reserved = reserved
