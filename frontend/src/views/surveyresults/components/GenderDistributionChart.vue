<template>
  <canvas ref="genderDistElem"></canvas>
</template>

<script setup lang="ts">
import { Chart, Title, Tooltip } from "chart.js";
import type { ChartConfiguration, Plugin } from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import _ from "lodash";
import type { AnyObject } from "chart.js/types/basic";
import { Gender } from "@/util/data";
import { onMounted, ref } from "vue";

// IMPORTANT: Make sure to load this component only after genderDistribution is not undefined/null!

const props = defineProps<{
  genderDistribution: Record<Gender, number>;
}>();

const genderDistElem = ref<HTMLCanvasElement | null>(null);


onMounted(() => loadChart());

function loadChart(): void {
  const textColor = "#080421";
  const chartDataColor = "#537cf9";
  const chartGridColor = "#cce";
  function chartPercentageFormatter(value: string | number) {
    return value + "%";
  }

  const maxAge = _.max(Object.values(props.genderDistribution));
  if (maxAge == null) {
    throw ReferenceError('maxAge was null or undefined');
  }

  const chartElem = genderDistElem.value;
  if (chartElem == null) {
    throw new TypeError("Could not find the chart DOM element");
  }

  const chartConfig: ChartConfiguration<'bar', number[], string> = {
    plugins: [ChartDataLabels, Title, Tooltip] as Plugin<'bar', AnyObject>[],
    type: 'bar',
    data: {
      labels: Object.keys(props.genderDistribution).map(k => {
        switch (k.toUpperCase()) {
          case Gender.MALE:
            return 'Male';
          case Gender.FEMALE:
            return 'Female';
          case Gender.OTHER:
            return 'Other';
          default:
            throw RangeError('Received unknown value: ' + k);
        }
      }),
      datasets: [{
        label: 'Percentage of responders',
        data: Object.values(props.genderDistribution),
      }],
    },
    options: {
      color: textColor,
      backgroundColor: chartDataColor,
      borderColor: chartGridColor,
      plugins: {
        datalabels: {
          align: 'top',
          anchor: 'end',
          color: textColor,
          offset: 2,
          formatter: value => chartPercentageFormatter(value.toFixed(2)),
        },
        title: {
          display: true,
          text: 'Gender distribution',
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
            display: false,
          },
        },
        y: {
          max: 100,
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