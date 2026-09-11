class HostsResponse(object):
    def __init__(self, address, ip_address=None, reserved=False):
        self.address = address
        self.used = ip_address is not None
        self.reserved = reserved
        self.ip_address_id = ip_address.pk if ip_address else None
