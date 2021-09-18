import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

import "@/assets/main.scss";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap";

axios.defaults.baseURL = '/';

createApp(App).use(router).mount('#app');
