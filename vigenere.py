key = "DECEPTIVE"
msg = "WEAREDISCOVEREDSAVEYOURSELF"

def sub(a,b):
    A = ord(a)-ord('A')
    B = ord(b)-ord('A')
    return chr((A+B)%26+ord("A"))

def revSub(a,b):
    A = ord(a)-ord('A')
    B = ord(b)-ord('A')
    return chr((A-B+26)%26+ord("A"))

def encrypt(msg, key,f = sub):
    msg = msg.upper()
    key = key.upper()
    ind = 0

    cipher = ""
    for i in msg:
        cipher += f(i,key[ind])
        ind = (ind+1)%len(key)

    return cipher

def decrypt(cipher,key):
    return encrypt(cipher,key,revSub)


if __name__ == '__main__':
    cipher = encrypt(msg,key)
    print(cipher)
    plainText = decrypt(cipher,key)
    print(plainText)