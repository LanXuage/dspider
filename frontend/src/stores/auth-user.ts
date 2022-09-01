import { User } from '@/api'
import { defineStore } from 'pinia'

const useAuthUserStore = defineStore({
    id: 'authUser',
    state: () => ({
        user: User.getUser()
    }),
    getters: {
        getToken: (state) => state.user.getToken,
        getUser: (state) => (state.user)
    },
    actions: {
        setUser(user: User) {
            this.user = user
        }
    }
})

export default useAuthUserStore
