import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'default-passive-events'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import i18n from './lang'

const app = createApp(App)

app.use(createPinia())
app.use(i18n)
app.use(ElementPlus)
app.use(router)

app.mount('#app')
