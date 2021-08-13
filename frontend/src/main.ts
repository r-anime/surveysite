import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

import "@/assets/main.scss"
import "bootstrap"

axios.defaults.baseURL = 'http://127.0.0.1:8000/'

createApp(App).use(router).mount('#app')
