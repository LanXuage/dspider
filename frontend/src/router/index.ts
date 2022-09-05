import NProgress from 'nprogress'
import { createRouter, createWebHashHistory } from 'vue-router'

import 'nprogress/nprogress.css'
import { useAuthUserStore } from '@/stores'

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'Login',
            component: () => import('@/pages/Login.vue'),
            meta: {
                requiresAuth: false
            }
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            component: () => import('@/pages/NotFound.vue'),
            meta: {
                requiresAuth: false
            }
        },
        {
            path: '/',
            name: 'Home',
            component: () => import('@/pages/Layout.vue'),
            redirect: 'dashboard',
            meta: {
                requiresAuth: true
            },
            children: [
                {
                    path: 'dashboard',
                    name: 'pages_dashboard',
                    component: () => import('@/pages/Dashboard.vue'),
                    meta: {
                        requiresAuth: true,
                    }
                }
            ]
        }
    ]
})

let loggedInBlacklist = ['/login']

router.beforeEach((to, from, next) => {
    NProgress.start()
    const authUser = useAuthUserStore()
    if (authUser.token) {
        if (loggedInBlacklist.includes(to.path)) {
            next(from)
        } else {
            authUser.getRoute().forEach(route => router.addRoute('Home', route))
            next()
        }
    } else {
        if (to.matched.length > 0 && !to.matched.some(record => record.meta.requiresAuth)) {
            next()
        } else {
            next({ name: 'Login' })
        }
    }
})

router.afterEach((to, from) => {
    NProgress.done()
})

export default router
