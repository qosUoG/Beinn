"""Exceptions inn cnoc library

For examples of using the exception, please refer to examples in
example/examplelib.

This module provides exception useful for user when writing experiment class

    * ExperimentEnded - Exception indicating the expeiriment is ended
        This exception shall be raised in loop method of the definition of
        experiment class
"""


class ExperimentEnded(Exception):
    pass
