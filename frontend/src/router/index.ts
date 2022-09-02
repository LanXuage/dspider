import NProgress from 'nprogress'
import { createRouter, createWebHistory } from 'vue-router'

import 'nprogress/nprogress.css'
import { useAuthUserStore } from '@/stores'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: {
                requiresAuth: false
            }
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
