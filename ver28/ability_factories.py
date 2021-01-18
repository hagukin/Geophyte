from ability import Ability
from components import activatable
from order import AbilityOrder

####################
###### SPELLS ######
####################

### Lightning Bolt
lightning_bolt = Ability(
    name="lightning bolt",
    ability_id="m_lightning_bolt",
    ability_desc="When the spell is casted, a lightning bolt will strike a random actor in sight.",
    ability_type=AbilityOrder.REGULAR_SPELL,
    activatable=activatable.LightningStrikeActivatable(
        mana_cost=30,
        difficulty=1,
        damage=30,
        maximum_range=99,
    )
)

####################
###### SKILLS ######
####################

### Steal
steal = Ability(
    name="steal",
    ability_id="sk_steal",
    ability_desc="By performing this action, you will be able to steal random items from your opponents.",
    ability_type=AbilityOrder.REGULAR_SKILL,
    activatable=activatable.StealActivatable()
)