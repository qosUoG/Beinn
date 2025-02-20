from typing import Literal, TypedDict


class AvailableEquipmentOutMessage(TypedDict):
    command: Literal["Load-Equipment"]

    # name: address of equipment
    payload: dict[str, str]


type WsOutTypeUnion = AvailableEquipmentOutMessage
