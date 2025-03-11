from dataclasses import dataclass
import math
from typing import ClassVar, TypedDict
from qoslablib import runtime as r, params as p

"""
@dataclass decorator allow us to type hint the type of the class,
this way, combined with the ParamsType TypedDict and the params type hint,
consumer of this class may get intellisense easily.

Note that with @dataclass prescence, the attributes declared: "params: ParamsType",
is considered instance attribute instead of class attribute.

For class attribute, one must wrap the type with ClassVar like "equipment_pi",
"equipment_model" below
"""


@dataclass
class ExampleEquipment(r.EquipmentABC):
    class ParamsType(TypedDict):
        strparam: p.StrParam
        floatparam: p.FloatParam
        intparam: p.IntParam
        boolparam: p.BoolParam
        selectstrparam: p.SelectStrParam
        selectintparam: p.SelectIntParam
        selectfloatparam: p.SelectFloatParam

    params: ParamsType

    # These ClassVars are class attributes instead of instance attributes
    # One would need to acquire it by ExampleEquipment.equipment_pi, instead
    # of through the equipment instance
    equipment_pi: ClassVar[float] = math.pi
    equipment_model: ClassVar[str] = "QOS007"

    def __init__(self):
        # Step 1. Call Super
        super.__init__(self)

        # Default params list
        self.params: ExampleEquipment.ParamsType = {
            "strparam": p.str_param(),
            "floatparam": p.float_param(suffix="W"),
            "intparam": p.int_param(),
            "boolparam": p.bool_param(False),
            "selectstrparam": p.select_str_param(["option1", "option2", "option3"]),
            "selectintparam": p.select_int_param([1, 2, 3]),
            "selectfloatparam": p.select_float_param([1.1, 2.2, 3.3]),
        }

        # # After the params list, one shall instantiate the equipment instance if needed
        # # using corresponding libraries, such as pyvisa, pyserial, zhinst.toolkit etc
        # # The example below is adapted from pyvisa official doc

        # rm = pyvisa.ResourceManager()
        # self.equipment = rm.open_resource('GPIB0::12::INSTR')
        # ...

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
    @r.EquipmentTLock
    @property
    def amplitude(self):
        # # In real life one should do something with the equipment
        # return self.equipment.measure()

        return self.amplitude

    # The setter is triggered when some value is assigned to the "amplitude" property
    # The value assigned is passed as the second argument in the parameter list,
    # "value" for the example below

    @r.EquipmentTLock
    @amplitude.setter
    def amplitude_setter(self, input: int):
        self.amplitude = input

    # For actions that isn't a property, such as one off movement of a spectrometer turret, one
    # may write a normal function
    @r.EquipmentTLock
    def echo(self, input: str):
        return input
