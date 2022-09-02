import { User } from '@/api'
import { Cypher } from '@/utils'
import { defineStore } from 'pinia'

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
        }
    }
})

export default useAuthUserStore
