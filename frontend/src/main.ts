import "@/assets/main.scss";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap";

import { BarController, BarElement, CategoryScale, Chart, LinearScale, Tooltip } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

Chart.register(CategoryScale, LinearScale, BarController, BarElement, ChartDataLabels, Tooltip);

createApp(App).use(router).mount('#app');
