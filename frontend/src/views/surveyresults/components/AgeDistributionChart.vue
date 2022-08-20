<template>
  <canvas ref="ageDistElem"></canvas>
</template>

<script setup lang="ts">
import { Chart, Title, Tooltip } from "chart.js";
import type { ChartConfiguration, Plugin } from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import _ from "lodash";
import type { AnyObject } from "chart.js/types/basic";
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

  const maxAge = _.max(Object.values(props.ageDistribution));
  if (maxAge == null) {
    throw TypeError('maxAge was null or undefined');
  }

  const chartElem = ageDistElem.value;
  if (chartElem == null) {
    throw new TypeError("Could not find the chart DOM element");
  }

  const chartConfig: ChartConfiguration<'bar', number[], number> = {
    plugins: [ChartDataLabels, Title, Tooltip] as Plugin<'bar', AnyObject>[],
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
          max: Math.round(maxAge * 1.1 + 0.5),
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