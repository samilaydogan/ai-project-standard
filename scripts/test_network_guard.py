"""Reference-suite loopback-only transport guard, including child Python processes."""

import ipaddress
import socket

_original_resolve = socket.getaddrinfo
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_original_sendto = socket.socket.sendto


def allowed(host):
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except (ValueError, TypeError):
        return False


def resolve(host, *args, **kwargs):
    if host is not None and not allowed(host):
        raise PermissionError("Reference tests deny non-loopback DNS/network")
    return _original_resolve(host, *args, **kwargs)


def connect(self, address):
    if self.family in {socket.AF_INET, socket.AF_INET6} and not allowed(address[0]):
        raise PermissionError("Reference tests deny non-loopback network")
    return _original_connect(self, address)


def connect_ex(self, address):
    if self.family in {socket.AF_INET, socket.AF_INET6} and not allowed(address[0]):
        raise PermissionError("Reference tests deny non-loopback network")
    return _original_connect_ex(self, address)


socket.getaddrinfo = resolve
socket.socket.connect = connect
socket.socket.connect_ex = connect_ex


def sendto(self, data, *args):
    address = args[-1]
    if self.family in {socket.AF_INET, socket.AF_INET6} and not allowed(address[0]):
        raise PermissionError("Reference tests deny non-loopback datagrams")
    return _original_sendto(self, data, *args)


socket.socket.sendto = sendto
