from ability import Ability
from components import activatable
from order import AbilityOrder
from language import interpret as i

import anim_graphics

####################
###### SPELLS ######
####################

### Lightning Bolt
lightning_bolt = Ability(
    name=i("뇌격",
           f"lightning bolt"),
    ability_id="sp_lightning_bolt",
    ability_desc=i("시야 내의 임의의 생명체 위에 번개가 떨어집니다.",
                   f"When casted, a lightning bolt will strike a random creature in sight."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.LightningStrikeActivatable(
        mana_cost=50,
        difficulty=1,
        damage=30,
        maximum_range=99,
    )
)

### Spectral beam
spectral_beam = Ability(
    name=i("분광 광선",
           f"spectral beam"),
    ability_id="sp_spectral_beam",
    ability_desc=i("형형색색의 빛으로 이루어진 강력한 마법 광선을 발사합니다.",
                   f"You can fire a powerful ray of light."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.SpectralBeamActivatable(mana_cost=50, difficulty=0, penetration=False, damage_range=(25,60), anim_graphic=anim_graphics.spectral_beam, stack_anim_frame=True)
)

### Soul bolt
soul_bolt = Ability(
    name=i("소울 볼트",
           f"soul bolt"),
    ability_id="sp_soul_bolt",
    ability_desc=i("상대의 영혼을 공격할 수 있는 마법 탄환을 발사합니다.",
                   f"You can cast a magical bolt which torments the target's soul."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.SoulBoltActivatable(mana_cost=30, difficulty=0, penetration=True, damage_range=(10,20), anim_graphic=anim_graphics.soul_bolt, stack_anim_frame=False)
)

### Call of the Orc Lord
call_of_the_orc_lord = Ability(
    name=i("오크 족장의 부름",
           f"call of the orc lord"),
    ability_id="sp_call_of_the_orc_lord",
    ability_desc=i("던전 전체에 울리는 강력한 포효를 내질러 오크 종족들에게 공격 명령을 내립니다.",
                   f"You can command orcs in the same level to attack a specific target."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.CallOfTheOrcLordActivatable(mana_cost=100, difficulty=0)
)

### cure wound
cure_wound = Ability(
    name=i("상처 치유",
           f"cure wound"),
    ability_id="sp_cure_wound",
    ability_desc=i("선택한 대상의 상처를 치유할 수 있습니다.",
                   f"You can magically cure target's wound."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.CureWoundActivatable(mana_cost=40, difficulty=0, heal_range=(10,30))
)

### mesmerize
mesmerize = Ability(
    name=i("매혹",
           f"mesmerize"),
    ability_id="sp_mesmerize",
    ability_desc=i("선택한 대상을 매혹시켜 아군으로 만들 수 있습니다.",
                   f"You can mesmerize the target and make it into your ally."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.MesmerizeSpellActivatable(mana_cost=105, difficulty=0)
)

### teleport
teleport = Ability(
    name=i("순간이동",
           f"teleport"),
    ability_id="sp_teleport",
    ability_desc=i("선택한 위치로 순간이동합니다.",
                   f"You can teleport."),
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.TeleportSpellActivatable(mana_cost=100, difficulty=0)
)

####################
###### SKILLS ######
####################

### Steal
steal = Ability(
    name=i("훔치기",
           f"steal"),
    ability_id="sk_steal",
    ability_desc=i("상대방으로부터 일정 확률로 임의의 아이템 한 가지를 빼앗아옵니다.",
                   f"You can steal a random item from the target."),
    ability_type=AbilityOrder.REGULAR_SKILL,
    activatable=activatable.StealActivatable()
)
