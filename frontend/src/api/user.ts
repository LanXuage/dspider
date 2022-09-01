import i18n from '@/lang'
import { useAuthUserStore } from '@/stores'
import { Msg, Req } from '@/utils'
import { AxiosError } from 'axios'
import { Base64 } from 'js-base64'


class User {
    private id: number
    private username: string
    private token: string

    constructor(username: string) {
        this.id = 0
        this.username = username
        this.token = ''
    }

    getToken(): string {
        return this.token
    }

    static encode(user: User): string {
        return Base64.encode(JSON.stringify(user))
    }

    static decode(userEnc: string | null): User {
        return userEnc ? Object.assign(new User(''), JSON.parse(Base64.decode(userEnc))) : new User('')
    }

    static getUserEnc(): string {
        let userEnc = sessionStorage.getItem('user')
        return userEnc ? userEnc : ''
    }

    async login(password: string): Promise<boolean> {
        try {
            let { token } = await Req.post('api-token-auth/', {
                username: this.username,
                password: password
            })
            this.token = token
            let userEnc = User.encode(this)
            const authUser = useAuthUserStore()
            authUser.setUser(userEnc)
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