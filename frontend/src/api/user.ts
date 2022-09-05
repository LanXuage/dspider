import i18n from '@/lang'
import { Msg, Req } from '@/utils'
import { AxiosError } from 'axios'
import type Page from './page'


class User {
    id: number | null = null
    username: string | null = null
    first_name: string | null = null
    last_name: string | null = null
    email: string | null = null
    token: string | null = null
    last_login: Date | null = null
    pages: Array<Page> | null = null

    constructor(username: string | null = null) {
        this.username = username
    }

    async login(password: string): Promise<boolean> {
        try {
            let user = await Req.post('api-token-auth/', {
                username: this.username,
                password: password
            })
            Object.assign(this, user)
            if (!this.token) {
                throw new Error()
            }
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