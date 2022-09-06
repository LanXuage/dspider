import type { RouteRecordRaw } from 'vue-router'

const routesMap: { [key: string]: RouteRecordRaw } = {
    pages_dashboard: {
        path: 'dashboard',
        name: 'pages_dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: {
            requiresAuth: true,
        }
    },
    pages_about: {
        path: 'about',
        name: 'pages_about',
        component: () => import('@/pages/About.vue'),
        meta: {
            requiresAuth: true
        }
    },
    pages_task_center: {
        path: 'task',
        name: 'pages_task_center',
        component: () => import('@/pages/TaskCenter.vue'),
        meta: {
            requiresAuth: true
        }
    }
}
export default routesMap
