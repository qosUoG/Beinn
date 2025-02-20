from typing import Literal, TypedDict


class LoadEquipmentInMessage(TypedDict):
    class LoadEquipmentPayload(TypedDict):
        address: str
        path: str
        classname: str

    command: Literal["Load-Equipment"]

    # name: info of equipment
    payload: dict[str, LoadEquipmentPayload]


type WsInMessageTypeUnion = LoadEquipmentInMessage
