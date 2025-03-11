import { type RouteType } from "../lib/_shared"
import { routes as workspaceRoutes } from "./workspace/index"
export const routes: RouteType = {
    ...workspaceRoutes
}
