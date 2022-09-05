import { User } from '@/api'
import { Cypher, Route } from '@/utils'
import { defineStore } from 'pinia'
import type { RouteRecordRaw } from 'vue-router'

const useAuthUserStore = defineStore({
    id: 'authUser',
    state: () => ({
        userEnc: sessionStorage.getItem('user')
    }),
    getters: {
        user: (state) => Cypher.decode<User>(state.userEnc, User),
        token: (state) => Cypher.decode<User>(state.userEnc, User).token,
    },
    actions: {
        setUser(user: User) {
            this.userEnc = Cypher.encode(user)
            sessionStorage.setItem('user', this.userEnc)
        },
        async login({ username, password }: { username: string, password: string }): Promise<boolean> {
            let user = new User(username)
            let ret = await user.login(password)
            this.setUser(user)
            return ret
        },
        getRoute(): Array<RouteRecordRaw> {
            return Route.getRoutes(this.user)
        }
    }
})

export default useAuthUserStore
