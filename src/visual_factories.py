import random
import skin_factories

from visual import Visual

def v_magic_missile(x: int, y: int, randomize=True):
    tile = Visual(
        x=x,
        y=y,
        char='*',
        skin=skin_factories.skin_magic_missile(randomize),
        fg=(230, 10, 90),
        bg=(255, 90, 90),
    )
    return tile


def v_piercing_flame(x: int, y: int, randomize=True):
    tile = Visual(
        x=x,
        y=y,
        char='*',
        skin=skin_factories.skin_piercing_flame(randomize),
        fg=(255, 89, 0),
        bg=(255, 208, 0),
    )
    return tile

def v_explosion(x: int, y: int, randomize=True):
    if randomize:
        fgs = (
            (245, 231, 78),
            (251, 255, 185),
            (249, 199, 46),
            (236, 74, 46)
        )
        fg = random.choice(fgs)
    else:
        fg = (251, 255, 185)

    tile = Visual(
        x=x,
        y=y,
        char='*',
        skin=skin_factories.skin_explosion(randomize),
        fg=fg,
        bg=None,
    )
    return tile


def v_acid_explosion(x: int, y: int, randomize=True):
    if randomize:
        fgs = (
            (176, 191, 26),
            (117, 191, 21),
            (186, 191, 27),
            (152, 191, 44)
        )
        fg = random.choice(fgs)
    else:
        fg = (117, 191, 21)

    tile = Visual(
        x=x,
        y=y,
        char='*',
        skin=skin_factories.skin_acid_explosion(randomize),
        fg=fg,
        bg=None,
    )
    return tile
