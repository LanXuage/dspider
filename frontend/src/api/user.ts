import i18n from '@/lang'
import { useAuthUserStore } from '@/stores'
import { Msg, Req } from '@/utils'
import { AxiosError } from 'axios'


class User {
    id: number
    username: string
    token: string

    constructor(username: string = '') {
        this.id = 0
        this.username = username
        this.token = ''
    }

    async login(password: string): Promise<boolean> {
        try {
            let { token } = await Req.post('api-token-auth/', {
                username: this.username,
                password: password
            })
            this.token = token
            const authUser = useAuthUserStore()
            authUser.setUser(this)
            Req.setToken(this.token)
            Msg.success(i18n.global.t('loginSuccess'))
            return true
        } catch (error) {
            if (error instanceof AxiosError && error.code == AxiosError.ERR_BAD_RESPONSE) {
                Msg.error(error.message)
            } else {
                Msg.warning(i18n.global.t('incorrectUnameOrPass'))
            }
            return false
        }
    }

}

export default User