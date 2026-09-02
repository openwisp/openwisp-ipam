class HostsResponse(object):
    def __init__(self, address, ip_address=None, reserved_subnet=None):
        self.address = address
        self.used = ip_address is not None
        self.reserved = reserved_subnet is not None
        self.ip_address_id = ip_address.pk if ip_address else None
        self.reserved_subnet_id = reserved_subnet.pk if reserved_subnet else None
