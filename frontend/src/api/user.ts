import i18n from '@/lang'
import { Msg } from '@/utils/msg'
import { Req } from '@/utils/net'
import { AxiosError } from 'axios'
import { Base64 } from 'js-base64'


class User {
    private username: string
    private password: string
    private token: string

    constructor({ username, password }: { username: string, password: string }) {
        this.username = username
        this.password = password
        this.token = ''
    }

    getToken(): string {
        return this.token
    }

    async login(): Promise<boolean> {
        try {
            let { token } = await Req.post('api-token-auth/', {
                username: this.username,
                password: this.password
            })
            this.token = token
            this.password = ''
            sessionStorage.setItem('user', Base64.encode(JSON.stringify(this)))
            Req.setToken(this.token)
            Msg.success(i18n.global.t('loginSuccess'))
            return true
        } catch (error) {
            if (error instanceof AxiosError && error.code == AxiosError.ERR_BAD_RESPONSE) {
                Msg.error(error.message)
            } else {
                Msg.warning('用户名或密码错误！')
            }
            return false
        }
    }

}

export { User }