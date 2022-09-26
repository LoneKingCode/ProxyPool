from enum import IntEnum


class ProxyProtocol(IntEnum):
    http = 0,
    https = 1,
    http_https = 2,
