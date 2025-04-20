"""Base Class of Experiment, Experiment Manger

For examples of defining experiment class (scripts), please refer to examples in
example/examplelib.

    * Experiment - Base class of all experiment scripts
        Users shall define experiment scripts by using ExperimentABC as the base class.

"""

from abc import ABC, abstractmethod
from .managers import ManagerABC


class ExperimentABC(ABC):
    """
    Base class of all experiment scripts

    Attributes
    ----------
    params : .params.Params
        a dictionary of parameters accessible by the experiment script

    """

    # Instance shall initiate params in __init__() function

    def __init__(self):
        """
        No parameters shall be passed to the __init__ function.

        Implementation of drivers shall also make sure to instantiate the
        self.params attribute as well.

         To be type safe, implementors may also define a params type specific
        to the experiment script. Detail please refer to example/experiment
        """
        from .params import Params

        self.params: Params

    @abstractmethod
    def initialize(self, manager: ManagerABC) -> int:
        """
        Always ran once before looping the loop method of the script

        This method is invoked after the start button of an experiment is pressed.
        self.params is finalized to the parameters set in the frontend when
        this method is invoked.
        As such, users shall define all variables that is going to be used by the loop
        method.

        For examples of using the manager instance, please refer to exampple/experiment

        Parameters
        ----------
        manager: ManagerABC
            The manager instance provided by the framework during runtime. Users shall setup
            all extensions (chart, savers) and suggestTotalIterations(int) if the number of loop
            can be calculated.

        """
        raise NotImplementedError

    @abstractmethod
    def loop(self, index: int):
        """
        Continuously invoked after the initialize method is invoked'

        When the experiment has ran it's last loop, a cnoc.exception.ExperimentEnded exception shall
        be raised to indicate the completion of the experiment

        For examples of using the index, please refer to example/experiment


        Parameters
        ----------
        index: int
            The index of current loop is passed such that users may choose the value to be
            used in the current loop
        """
        raise NotImplementedError

    def stop(self):
        """
        Perform any clean up if needed

        This method would run once after the loop method is no longer iterating. Users may perform
        any clean up in this method. However, please be aware other experiment script may stil be running

        It is optional to implement this method.
        """
        pass
