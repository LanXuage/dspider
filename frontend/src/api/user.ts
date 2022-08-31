import { Msg } from '@/utils/msg'
import { Req } from '@/utils/net'
import { Base64 } from 'js-base64'

class User {
    private static NF_ERROR = 'non_field_errors'

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
            Msg.success('登录成功！')
            return true
        } catch (error) {
            Msg.warning('登录失败！')
            return false
        }
    }

}

export { User }