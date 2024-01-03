import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

from django.db import models

from tictactoe.exceptions import SlotNotAvailableError, SlotOutOfRangeError


class FieldDescriptor:

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # The instance dict contains whatever was originally assigned in
        # __set__.
        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)
        return value

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = self.to_python(value)

    def to_python(self, value):
        raise NotImplementedError()


class Symbol(Enum):
    X = 'X'
    O = 'O'
    N = None


class SymbolDescriptor(FieldDescriptor):

    def to_python(self, value):
        if isinstance(value, Symbol):
            return value
        return Symbol(value)


class SymbolField(models.CharField):
    descriptor_class = SymbolDescriptor

    description = 'Symbol'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 1)
        kwargs['default'] = None
        super().__init__(*args, **kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Perform preliminary non-db specific value checks and conversions.
        """
        return value.value if isinstance(value, Symbol) else value

    def from_db_value(self, value, expression, connection):
        return Symbol(value)

    def to_python(self, value):
        if isinstance(value, Symbol):
            return value
        return Symbol(value)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))


@dataclass
class Slot:
    coords: Tuple[int, int]
    symbol: Symbol


class Board:

    rows: List[List[Symbol]]

    def __init__(self, rows: List[List[Symbol]]):
        self.rows = rows

    def __str__(self):
        return self.serialize()

    @property
    def as_list(self):
        return json.loads(self.serialize())

    def add_symbol(self, x: int, y: int, value: Symbol):
        try:
            if self.rows[x][y] != Symbol.N:
                raise SlotNotAvailableError()

            self.rows[x][y] = value
        except IndexError:
            raise SlotOutOfRangeError()

    def has_series_complete(self, symbol: Symbol):
        for series in self.get_series():
            if self.get_series_count(series, symbol) == 3:
                return True
        return False

    @property
    def is_full(self):
        return not any(slot.symbol == Symbol.N for series in self.get_series() for slot in series)

    def get_series(self):
        for row in self.row_slots:
            yield row
        for column in self.column_slots:
            yield column
        for diagonal in self.diagonal_slots:
            yield diagonal

    @staticmethod
    def get_series_count(series: List[Slot], symbol: Symbol):
        return len(list(filter(lambda s: s.symbol == symbol, series)))

    @property
    def row_slots(self):
        return [
            [
                Slot(coords=(0, 0), symbol=self.rows[0][0]),
                Slot(coords=(0, 1), symbol=self.rows[0][1]),
                Slot(coords=(0, 2), symbol=self.rows[0][2])
            ],
            [
                Slot(coords=(1, 0), symbol=self.rows[1][0]),
                Slot(coords=(1, 1), symbol=self.rows[1][1]),
                Slot(coords=(1, 2), symbol=self.rows[1][2])
            ],
            [
                Slot(coords=(2, 0), symbol=self.rows[2][0]),
                Slot(coords=(2, 1), symbol=self.rows[2][1]),
                Slot(coords=(2, 2), symbol=self.rows[2][2])
            ]
        ]

    @property
    def column_slots(self):
        return [
            [
                Slot(coords=(0, 0), symbol=self.rows[0][0]),
                Slot(coords=(1, 0), symbol=self.rows[1][0]),
                Slot(coords=(2, 0), symbol=self.rows[2][0])
            ],
            [
                Slot(coords=(0, 1), symbol=self.rows[0][1]),
                Slot(coords=(1, 1), symbol=self.rows[1][1]),
                Slot(coords=(2, 1), symbol=self.rows[2][1])
            ],
            [
                Slot(coords=(0, 2), symbol=self.rows[0][2]),
                Slot(coords=(1, 2), symbol=self.rows[1][2]),
                Slot(coords=(2, 2), symbol=self.rows[2][2])
            ]
        ]

    @property
    def diagonal_slots(self):
        return [
            [
                Slot(coords=(0, 0), symbol=self.rows[0][0]),
                Slot(coords=(1, 1), symbol=self.rows[1][1]),
                Slot(coords=(2, 2), symbol=self.rows[2][2])
            ],
            [
                Slot(coords=(0, 2), symbol=self.rows[0][2]),
                Slot(coords=(1, 1), symbol=self.rows[1][1]),
                Slot(coords=(2, 0), symbol=self.rows[2][0])
            ]
        ]

    def serialize(self):
        return json.dumps([
            [symbol.value for symbol in row]
            for row in self.rows
        ])

    @classmethod
    def deserialize(cls, value):
        return cls([
            [Symbol(x) for x in row]
            for row in json.loads(value)
        ])


class BoardDescriptor(FieldDescriptor):

    def to_python(self, value):
        if isinstance(value, Board):
            return value

        return Board([
            [Symbol(x) for x in row]
            for row in value
        ])


class BoardField(models.Field):
    descriptor_class = BoardDescriptor

    description = 'Board'

    def __init__(self, *args, **kwargs):
        kwargs['default'] = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        super().__init__(*args, **kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Perform preliminary non-db specific value checks and conversions.
        """
        return value.serialize() if isinstance(value, Board) else value

    def from_db_value(self, value, expression, connection):
        return Board.deserialize(value)

    def to_python(self, value):
        if isinstance(value, Board):
            return value
        return Board.deserialize(value)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def get_internal_type(self):
        return "TextField"
