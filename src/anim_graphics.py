import random

### Magical Ray
magic_missile = {
    "char":"*",
    "fg":(230, 10, 90),
    "bg":(255, 90, 90),
}

### Scorching ray
scorching_ray = {
    "char":"*",
    "fg":(255, 89, 0),
    "bg":(255, 208, 0),
}

### Freezing Ray
freezing_ray = {
    "char":"*",
    "fg":(66, 236, 255),
    "bg":(196, 249, 255),
}

### Digging Ray
digging_ray = {
    "char":"*",
    "fg":(255, 255, 48),
    "bg":(117, 255, 175),
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


### Spectral Beam
def spectral_beam():

    bgs = (
        (0xFF, 0x66, 0x63),
        (0xFE, 0xB1, 0x44),
        (0xFD, 0xFD, 0x97),
        (0x9E, 0xE0, 0x9E),
        (0x9E, 0xC1, 0xCF),
        (0xCC, 0x99, 0xC9)
    )
    bg = random.choice(bgs)

    beam = {
        "char":"*",
        "fg":(255,255,255),
        "bg":bg,
    }

    return beam



### Soul bolt
def soul_bolt():

    bgs = (
        (46, 255, 123),
        (46, 255, 151),
        (46, 255, 185),
    )
    bg = random.choice(bgs)

    beam = {
        "char":"*",
        "fg":(255,255,255),
        "bg":bg,
    }

    return beam