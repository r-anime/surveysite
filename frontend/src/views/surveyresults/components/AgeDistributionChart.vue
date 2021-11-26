<template>
  <canvas ref="ageDist"></canvas>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { Chart, ChartConfiguration, CategoryScale, LinearScale, BarController, BarElement } from "chart.js";
import _ from "lodash";

Chart.register(CategoryScale, LinearScale, BarController, BarElement);

// Make sure to load this component only after ageDistribution is not undefined/null!
@Options({
  props: {
    ageDistribution: Object,
  },
})
export default class AgeDistributionChart extends Vue {
  ageDistribution!: Record<number, number>

  mounted() {
    this.loadChart();
  }

  private loadChart(): void {
    const textColor = "#080421";
    const chartDataColor = "#537cf9";
    const chartDatalabelColor = textColor;
    const chartGridColor = "#cce"
    function chartPercentageFormatter(value: string | number) {
        return value + "%";
    }

    const maxAge = _.max(Object.values(this.ageDistribution))!;

    const chartElem = this.$refs['ageDist'] as HTMLCanvasElement;
    const chartConfig: ChartConfiguration<'bar', number[], number> = {
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
          legend: {
            display: false,
          },
          title: {
            display: true,
            text: 'Age distribution',
          },
          tooltip: {
            callbacks: {
              label: tooltipItem => chartPercentageFormatter(tooltipItem.parsed.y),
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