
from decimal import Decimal

def makeSprite(
        sprite_type,
        starting_chunk,
        starting_position : tuple[int, int],
        starting_speed : tuple[int, int] = (Decimal(0), Decimal(0)),
        lifecycle_manager : str = 'PER_MAP',
        group : str = 'FRONT',
        **kwargs
        ):

    sprite_initializer = {
        'sprite_type': sprite_type.__name__,
        'starting_position': starting_position,
        'starting_speed': starting_speed,
        'lifecycle_manager': lifecycle_manager,
        'group': group
    }
    for arg_name, arg_value in kwargs.items():
        sprite_initializer[arg_name] = arg_value

    return sprite_type(sprite_initializer, starting_chunk)
