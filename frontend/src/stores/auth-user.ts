import { User } from '@/api'
import { defineStore } from 'pinia'

const useAuthUserStore = defineStore({
    id: 'authUser',
    state: () => ({
        user: sessionStorage.getItem('user')
    }),
    getters: {
        getToken: (state) => User.decode(state.user).getToken(),
        getUser: (state) => (state.user)
    },
    actions: {
        setUser(userEnc: string) {
            this.user = userEnc
            sessionStorage.setItem('user', userEnc)
        }
    }
})

export default useAuthUserStore
