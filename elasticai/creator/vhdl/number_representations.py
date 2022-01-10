from abc import ABC, abstractmethod
from functools import partial
from numbers import Integral, Rational
from typing import Union, Iterable, Any, overload


class FloatToSignedFixedPointConverter:
    """
    Create a fixed point representation as an unsigned int data type using two complements.

    We might want to have this create its own type `FixedPointNumber` in
    the future. That way we could make sure that the conversion is idempotent
    for numbers that are fixed point already.
    """

    def __init__(self, bits_used_for_fraction: int, strict=True):
        self.bits_used_for_fraction = bits_used_for_fraction
        self._strict = strict

    @property
    def one(self) -> int:
        return 1 << self.bits_used_for_fraction

    def __call__(self, x: float) -> int:
        x_tmp = float(x)
        x_tmp = x_tmp * self.one
        if not x_tmp.is_integer() and self._strict:
            raise ValueError(
                f"{x} not convertible to fixed point number using {self.bits_used_for_fraction} bits for fractional part"
            )
        return int(x_tmp)

    def to_string(self, x: float) -> str:
        return str(self.__call__(x))


class FloatToBinaryFixedPointStringConverter:
    def __init__(
        self,
        total_bit_width: int,
        as_signed_fixed_point: FloatToSignedFixedPointConverter,
    ):
        self.total_bit_width = total_bit_width
        self.as_signed_fixed_point = as_signed_fixed_point

    def __call__(self, x: Union[float, int]) -> str:
        signed_fixed_point = self.as_signed_fixed_point(x)
        return two_complements_representation(signed_fixed_point, self.total_bit_width)


def _int_to_bin_str(number: int, bits: int) -> str:
    return "{{0:0{number_of_bits}b}}".format(number_of_bits=bits).format(number)


def two_complements_representation(x, number_of_bits):
    if x < 0:
        unsigned_int_version = (1 << number_of_bits) + x
    else:
        unsigned_int_version = x
    return _int_to_bin_str(x, number_of_bits)


class ToLogicEncoder:
    """
    Throughout our implementations we have to deal with two different levels of representations for numbers:
    During training we typically need to apply mathematical operations and we do not care too much about how our numbers are encoded.
    E.g. in a scenario where we want to use two bit on hardware to represent our numbers, in our machine learning framework we
    might decide it is beneficial to use the numbers -3 and 4 for some reason. However, especially in the context of precomputed
    results, the hardware implementation does not need to know the numeric values, but instead just needs to be able to keep a
    consistent and correct mapping. The NumericToLogicEncoder takes care of performing the translations from numeric representation
    to the bit vector used in the hardware implementation. We encode bit vectors just as unsigned integers.
    """

    def __init__(self):
        self.numerics = set()
        self.mapping = dict()

    def add_numeric(self, numeric_representation: int) -> None:
        self.numerics.add(numeric_representation)
        self._update_mapping()

    def _update_mapping(self) -> None:
        length = len(self.numerics)
        sorted_numerics = list(self.numerics)
        sorted_numerics.sort()
        mapping = dict(((value, index) for index, value in enumerate(sorted_numerics)))
        self.mapping.update(mapping)

    def __getitem__(self, item: int) -> int:
        return self.mapping[item]


class BitVector:
    def __init__(self, number: int):
        self._number = int
