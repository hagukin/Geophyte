def hasBatchim(keyword: str) -> bool:
    if (ord(keyword[len(keyword) - 1]) - 0xAC00) % 28:
        return True
    else:
        return False

def grammar(keyword: str, word: str) -> str: #Short function name since its frequently used
    """
    keyword와 word 사이에 띄어쓰기가 없다고 간주한다.
    """
    batchim = hasBatchim(keyword)

    if word == "이" or word == "가":
        if batchim:
            return keyword + "이"
        else:
            return keyword + "가"
    elif word == "은" or word == "는":
        if batchim:
            return keyword + "은"
        else:
            return keyword + "는"
    elif word == "으로" or word == "로":
        if batchim:
            return keyword + "으로"
        else:
            return keyword + "로"
    elif word == "을" or word == "를":
        if batchim:
            return keyword + "을"
        else:
            return keyword + "를"
    elif word == '와' or word == '과':
        if batchim:
            return keyword + '과'
        else:
            return keyword + '와'
    elif word == '라' or word == '이라':
        if batchim:
            return keyword + '이라'
        else:
            return keyword + '라'
    elif word == '와'or word == '과':
        if batchim:
            return keyword + '과'
        else:
            return keyword + '와'
    else:
        raise NotImplementedError()
