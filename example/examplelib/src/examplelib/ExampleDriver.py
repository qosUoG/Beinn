import math
from random import random
from typing import TypedDict
from cnoc import params as p

from cnoc.equipment import EquipmentABC

"""
@dataclass decorator allow us to type hint the type of the class,
this way, combined with the ParamsType TypedDict and the params type hint,
consumer of this class may get intellisense easily.

Note that with @dataclass prescence, the attributes declared: "params: ParamsType",
is considered instance attribute instead of class attribute.

For class attribute, one must wrap the type with ClassVar like "equipment_pi",
"equipment_model" below
"""


class ExampleEquipment(EquipmentABC):
    class ParamsType(TypedDict):
        strparam: p.StrParam
        floatparam: p.FloatParam
        intparam: p.IntParam
        boolparam: p.BoolParam
        selectstrparam: p.SelectStrParam
        selectintparam: p.SelectIntParam
        selectfloatparam: p.SelectFloatParam

    # These are class attributes instead of instance attributes
    # While you may acquire it through the instance, it maybe easily mixed up
    equipment_pi: float = math.pi
    equipment_model: str = "QOS007"

    def __init__(self):
        # Default params list
        self.params: ExampleEquipment.ParamsType = {
            "strparam": p.StrParam(),
            "floatparam": p.FloatParam(suffix="W"),
            "intparam": p.IntParam(),
            "boolparam": p.BoolParam(False),
            "select_strparam": p.SelectStrParam(["option1", "option2", "option3"]),
            "select_intparam": p.SelectIntParam([1, 2, 3]),
            "select_floatparam": p.SelectFloatParam([1.1, 2.2, 3.3]),
        }

        # # After the params list, one shall instantiate the equipment instance if needed
        # # using corresponding libraries, such as pyvisa, pyserial, zhinst.toolkit etc
        # # The example below is adapted from pyvisa official doc

        # rm = pyvisa.ResourceManager()
        # self.equipment = rm.open_resource('GPIB0::12::INSTR')
        # ...
        # # Here, a private variable is ued for demonstration instead
        self._power: int = 0

        """
        __init__() shall only contain the above code.
        
        For Equipment specific constants that is shared among all equipment instance,
        you shall use @classmethod and class attribute instead.
        
        Imagine, two laser with same model would share the same model number,
        likewise two lockins SR830 would both share "SR830"
        
        See code above for examples
        
        HOWEVER, for functions common to all equipments, we do not implement them as classmethods,
        instead they should be bounded instance methods, bounded means you implicitly pass self as
        the first argument
        
        This is because even the behavior is the same, if you are using two lockins, they are two
        instances, thus calling the function should only work on one equipment, instead of both, or all
        instances of the equipment
        
        Instead, only use @classmethod for helper / util functions that is shared between all instances.
        
        For instance, all lockins or simply RC filters (lockin filters) shall share the same band width to
        settling time conversion relationship. As such, a function that is not performing operation on the 
        equipment instance shall be implemented with @classmethod. 
        
        See code at the end for examples (after the instance methods)
        
        """

    # Define equipment properties as follows:
    # @property decorator allows the instance method to be executed as if it is a instance attribute
    # In other words, it intercepts during instance attribute acquisition and assignment
    @property
    def power(self):
        # # In real life one should do something with the equipment,
        # # Which shall be acuired with pyvisa
        # return self.equipment.query("POW?")

        return self._power

    # The setter is triggered when some value is assigned to the "power" property
    # The value assigned is passed as the second argument in the parameter list,
    # "value" for the example below

    @power.setter
    def power(self, input: int):
        self._power = input

    # For actions that isn't a property, such as one off movement of a spectrometer turret, one
    # may write a normal function

    def echo(self, input: str):
        return input

    # While you may implement everything with @property, I like to define read only with methods and treat them as instead

    def measureTemp(self):
        return random() * 100 * self._power
