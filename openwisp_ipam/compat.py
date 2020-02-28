from ipaddress import IPv4Network, IPv6Network


def patch_ipaddress_lib():
    """
    On python < 3.7, the ipaddress library does not have
    the method ``subnet_of``, so we add it via monkey patching
    """
    def _is_subnet_of(a, b):
        try:
            # Always false if one is v4 and the other is v6
            if a._version != b._version:
                raise TypeError("%s and %s are not of the same version" % (a, b))
            return (b.network_address <= a.network_address and b.broadcast_address >= a.broadcast_address)
        except AttributeError:
            raise TypeError("Unable to test subnet containment "
                            "between %s and %s" % (a, b))

    def subnet_of(self, other):
        """ Return True if this network is a subnet of other """
        return self._is_subnet_of(self, other)

    if not hasattr(IPv4Network, 'subnet_of'):
        IPv4Network._is_subnet_of = staticmethod(_is_subnet_of)
        IPv4Network.subnet_of = subnet_of
    if not hasattr(IPv6Network, 'subnet_of'):
        IPv6Network._is_subnet_of = staticmethod(_is_subnet_of)
        IPv6Network.subnet_of = subnet_of
