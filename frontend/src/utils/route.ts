import { Page, User } from "@/api"
import routesMap from "@/router/routes"
import type { RouteRecordRaw } from "vue-router"

class Route {
    static getRoutes(node: Page | User): Array<RouteRecordRaw> {
        let ret: Array<RouteRecordRaw> = []
        let children : Array<Page> = []
        if (node instanceof Page && node.children) {
            children = node.children
        } else if (node instanceof User && node.pages) {
            children = node.pages
        }
        children.forEach((child) => {
            if (child.name) {
                let sub_node = routesMap[child.name]
                sub_node.children = Route.getRoutes(child)
                ret.push(sub_node)
            }
        })
        return ret
    }
}

export default Route
