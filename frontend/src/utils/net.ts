import axios from 'axios'
import NProgress from 'nprogress'

import 'nprogress/nprogress.css'

const instance = axios.create({
    baseURL: import.meta.env.VITE_BASE_URL,
    timeout: 30000,
})

// Add a request interceptor
instance.interceptors.request.use(function (config) {
        NProgress.start()
        return config;
    }, function (error) {
        NProgress.done()
        return Promise.reject(error);
    });

// Add a response interceptor
instance.interceptors.response.use(function (response) {
        NProgress.done()
        return response;
    }, function (error) {
        NProgress.done()
        return Promise.reject(error);
    });

export { instance }