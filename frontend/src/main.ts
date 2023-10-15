import "@/assets/main.scss";
import "bootstrap-icons/font/bootstrap-icons.css";

import { BarController, BarElement, CategoryScale, Chart, LinearScale, Title, Tooltip } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

Chart.register(CategoryScale, LinearScale, BarController, BarElement, ChartDataLabels, Title, Tooltip);

const app = createApp(App).use(router);
app.mount("#app");
