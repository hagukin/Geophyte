import random

### Magical Ray
magic_missile = {
    "char":"*",
    "fg":(230, 10, 90),
    "bg":(255, 90, 90),
}

### Piercing Flame
piercing_flame = {
    "char":"*",
    "fg":(255, 89, 0),
    "bg":(255, 208, 0),
}

### Explosion
def explosion():

    fgs = (
        (245, 231, 78),
        (251, 255, 185),
        (249, 199, 46),
        (236, 74, 46)
    )
    fg = random.choice(fgs)

    expl = {
        "char":"*",
        "fg":fg,
        "bg":None,
    }

    return expl


### Explosion
def acid_explosion():

    fgs = (
        (176,191,26),
        (117,191,21),
        (186,191,27),
        (152,191,44)
    )
    fg = random.choice(fgs)

    expl = {
        "char":"*",
        "fg":fg,
        "bg":None,
    }

    return expl