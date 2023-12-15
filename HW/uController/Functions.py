def listIntegersToByteArray(l:list, mode='little'):
    ll = l.copy()
    for i in range(0, len(ll)):
        ll[i] = ll[i].to_bytes(1, mode)
    bts = b''.join(ll)
    return bts