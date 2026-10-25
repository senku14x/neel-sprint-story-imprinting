import json
def bytes_to_unicode():
    bs=list(range(ord("!"),ord("~")+1))+list(range(ord("¡"),ord("¬")+1))+list(range(ord("®"),ord("ÿ")+1))
    cs=bs[:]; n=0
    for b in range(256):
        if b not in bs: bs.append(b); cs.append(256+n); n+=1
    return dict(zip(bs,[chr(c) for c in cs]))
_bd={v:k for k,v in bytes_to_unicode().items()}
_tj=json.load(open(__file__.rsplit('/',1)[0]+'/tokenizer.json'))
_inv={v:k for k,v in _tj['model']['vocab'].items()}
_special={a['id']:a['content'] for a in _tj.get('added_tokens',[])}
def decode(ids):
    out=bytearray()
    for i in ids:
        if i in _special: out+=_special[i].encode(); continue
        s=_inv[i]
        out+=bytes(_bd[c] for c in s)
    return out.decode('utf-8',errors='replace')
