import type { AxiosError } from 'axios'
import { instance } from '../utils/net'

class User {
    username: string
    password: string
    token: string
    errorMessage : string

    constructor(username: string, password: string) {
        this.username = username
        this.password = password
        this.token = ''
        this.errorMessage = ''
    }

    getToken(): string {
        return this.token
    }

    async login(): Promise<boolean> {
        try {
            let { data } = await instance.post('api-token-auth/', {
                username: this.username,
                password: this.password
            })
            this.token = data.token
            instance.defaults.headers.common['Authorization'] = 'token ' + this.token
            this.password = ''
        } catch (error) {
            let { response } = error as AxiosError
            response?.data
            return false
        }
        return true
    }

}

export { User }