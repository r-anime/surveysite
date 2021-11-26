<template>
  <canvas ref="ageDist"></canvas>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { Chart, ChartConfiguration, Plugin, Tooltip } from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import _ from "lodash";
import { AnyObject } from "chart.js/types/basic";

// Make sure to load this component only after ageDistribution is not undefined/null!
@Options({
  props: {
    ageDistribution: Object,
  },
})
export default class AgeDistributionChart extends Vue {
  ageDistribution!: Record<number, number>

  mounted(): void {
    this.loadChart();
  }

  private loadChart(): void {
    const textColor = "#080421";
    const chartDataColor = "#537cf9";
    const chartGridColor = "#cce";
    function chartPercentageFormatter(value: string | number) {
      return value + "%";
    }

    const maxAge = _.max(Object.values(this.ageDistribution));
    if (maxAge == null) {
      throw ReferenceError('maxAge was null or undefined');
    }

    const chartElem = this.$refs['ageDist'] as HTMLCanvasElement;
    const chartConfig: ChartConfiguration<'bar', number[], number> = {
      plugins: [ChartDataLabels, Tooltip] as Plugin<'bar', AnyObject>[],
      type: 'bar',
      data: {
        labels: Object.keys(this.ageDistribution).map(k => Number(k)),
        datasets: [{
          label: 'Percentage of responders',
          data: Object.values(this.ageDistribution),
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
          legend: {
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
}
</script>