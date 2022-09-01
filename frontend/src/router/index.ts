import NProgress from 'nprogress'
import { createRouter, createWebHistory } from 'vue-router'

import 'nprogress/nprogress.css'
import { useAuthUserStore } from '@/stores'
import { User } from '@/api'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Index',
            component: () => import('@/views/Index.vue')
        },
        {
            path: '/login',
            name: 'Login',
            component: () => import('@/views/Login.vue')
        }
    ]
})

const whiteList: string[] = []

router.beforeEach((to, from, next) => {
    NProgress.start()
    /*if (whiteList.indexOf(to.path) === -1) {
        let userEnc = sessionStorage.getItem('user')
        if (userEnc) {
            let user = User.decode(userEnc)
            useAuthUserStore().setUser(user)
            let token = user.getToken()
            if (!token) {
                next({ name: 'Login' })
                return
            } else if (to.path === '/login') {
                next(from)
                return
            }
        } else if (to.path === '/login') {
            next()
            return
        } else {
            next({ name: 'Login' })
            return
        }
    }*/
    next()
})

router.afterEach((to, from) => {
    NProgress.done()
})

export default router
