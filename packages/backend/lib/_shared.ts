import type { RouterTypes } from "bun"

export const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS, POST',
    'Access-Control-Allow-Headers': 'Content-Type',
}

export type RouteType = Record<string, RouterTypes.RouteValue<Response & string>>