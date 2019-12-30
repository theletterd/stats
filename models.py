from collections import namedtuple

Stat = namedtuple(
    'Stat',
    (
        'stat_id',
        'description',
        'value',
        'notes',
    ),
    defaults=('',)
)
