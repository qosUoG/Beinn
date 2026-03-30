from typing import Any, Callable, Coroutine, Mapping


from ._saver import Saver as _S


class Saver[T: Mapping[str, object]]:
    def __init__(
        self,
        dir: str,
        title: str,
        schema: type[T],
        run_coroutine_threadsafe: Callable[[Coroutine[Any, Any, Any]], None],
    ):
        self._saver = _S[T](dir, title, schema, run_coroutine_threadsafe)

    # Thread safe
    def save(self, data: T):
        self._saver.save(data)
