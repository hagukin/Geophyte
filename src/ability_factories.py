from ability import Ability
from components import activatable
from order import AbilityOrder

import anim_graphics

####################
###### SPELLS ######
####################

### Lightning Bolt
lightning_bolt = Ability(
    name="뇌격",
    ability_id="sp_lightning_bolt",
    ability_desc="시야 내의 임의의 생명체 위에 번개가 떨어집니다.",
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.LightningStrikeActivatable(
        mana_cost=30,
        difficulty=1,
        damage=30,
        maximum_range=99,
    )
)

### Spectral beam
spectral_beam = Ability(
    name="분광 광선",
    ability_id="sp_spectral_beam",
    ability_desc="형형색색의 빛으로 이루어진 강력한 마법 광선을 발사합니다.",
    ability_type=AbilityOrder.REGULAR_SKILL,
    activatable=activatable.SpectralBeamActivatable(mana_cost=30, difficulty=0, penetration=False, damage_range=(25,60), anim_graphic=anim_graphics.spectral_beam)
)

####################
###### SKILLS ######
####################

### Steal
steal = Ability(
    name="훔치기",
    ability_id="sk_steal",
    ability_desc="상대방으로부터 일정 확률로 임의의 아이템 한 가지를 빼앗아옵니다.",
    ability_type=AbilityOrder.REGULAR_SKILL,
    activatable=activatable.StealActivatable()
)
