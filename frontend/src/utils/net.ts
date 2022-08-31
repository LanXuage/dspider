import axios, { AxiosError } from 'axios'
import NProgress from 'nprogress'

import 'nprogress/nprogress.css'
import { Msg } from './msg';

class Req {
    private static instance = axios.create({
        baseURL: import.meta.env.VITE_BASE_URL,
        timeout: 30000,
    })

    static init(): void {
        // Add a request interceptor
        Req.instance.interceptors.request.use(function (config) {
            NProgress.start()
            return config;
        }, function (error) {
            NProgress.done()
            return Promise.reject(error);
        });
        // Add a response interceptor
        Req.instance.interceptors.response.use(function (response) {
            NProgress.done()
            return response;
        }, function (error) {
            NProgress.done()
            return Promise.reject(error);
        });
    }

    static setToken(token: string): void {
        Req.setHeaders('Authorization', 'token ' + token)
    }

    static setHeaders(key: string, value: string): void {
        Req.instance.defaults.headers.common[key] = value
    }

    static post(url: string, data: any) {
        return new Promise<{ token: string }>((resolve, reject) => Req.instance.post(url, data).then(res => {
            resolve(res.data)
        }).catch(error => {
            if (error.code == AxiosError.ERR_NETWORK) {
                Msg.error(error.message)
            } else {
                reject(error as AxiosError)
            }
        }))
    }

}

Req.init()

export { Req }