class config_eval_CRC32_checksum(config_base):
    mutable = 3

def eval_CRC32_checksum(param, current):
    if len(param) == 0:
        return ''

    import binascii

    return str(binascii.crc32(param[0].encode()))

# TESTS
# IN [ 'foobar' ]
# OUT '2666930069'
