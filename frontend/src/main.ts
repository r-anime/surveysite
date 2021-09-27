import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import "@/assets/main.scss";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap";

createApp(App).use(router).mount('#app');
