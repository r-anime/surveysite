<template>
  <canvas ref="ageDistElem"></canvas>
</template>

<script setup lang="ts">
import { Chart, Title, Tooltip } from "chart.js";
import type { ChartConfiguration } from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { onMounted, ref } from "vue";

// IMPORTANT: Make sure to load this component only after ageDistribution is not undefined/null!

const props = defineProps<{
  ageDistribution: Record<number, number>;
}>();

const ageDistElem = ref<HTMLCanvasElement | null>(null);

onMounted(() => loadChart());


function loadChart(): void {
  const textColor = "#080421";
  const chartDataColor = "#537cf9";
  const chartGridColor = "#cce";
  function chartPercentageFormatter(value: string | number) {
    return value + "%";
  }

  const maxAgePercentage = Math.max(...Object.values(props.ageDistribution));
  if (maxAgePercentage == null) {
    throw TypeError('maxAgePercentage was null or undefined');
  }

  const chartElem = ageDistElem.value;
  if (chartElem == null) {
    throw new TypeError("Could not find the chart DOM element");
  }

  const chartConfig: ChartConfiguration<'bar', number[], number> = {
    plugins: [ChartDataLabels, Title, Tooltip],
    type: 'bar',
    data: {
      labels: Object.keys(props.ageDistribution).map(k => Number(k)),
      datasets: [{
        label: 'Percentage of responders',
        data: Object.values(props.ageDistribution),
      }],
    },
    options: {
      color: textColor,
      backgroundColor: chartDataColor,
      borderColor: chartGridColor,
      plugins: {
        datalabels: {
          display: false,
        },
        title: {
          display: true,
          text: 'Age distribution',
        },
        tooltip: {
          callbacks: {
            label: tooltipItem => chartPercentageFormatter(tooltipItem.parsed.y.toFixed(2)),
          },
        },
      },
      scales: {
        x: {
          grid: {
            offset: false,
          },
        },
        y: {
          max: Math.round(maxAgePercentage * 1.1 + 0.5),
          min: 0,
          ticks: {
            callback: chartPercentageFormatter,
          },
        },
      },
    },
  };
  new Chart(chartElem, chartConfig);
}
</script>