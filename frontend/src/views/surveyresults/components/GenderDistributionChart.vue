<template>
  <canvas ref="genderDist"></canvas>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";
import { Chart, ChartConfiguration, Plugin, Title, Tooltip } from "chart.js";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import _ from "lodash";
import { AnyObject } from "chart.js/types/basic";
import { Gender } from "@/util/data";

// Make sure to load this component only after genderDistribution is not undefined/null!
@Options({
  props: {
    genderDistribution: {
      type: Object,
      required: true,
    },
  },
})
export default class GenderDistributionChart extends Vue {
  genderDistribution!: Record<Gender, number>

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

    const maxAge = _.max(Object.values(this.genderDistribution));
    if (maxAge == null) {
      throw ReferenceError('maxAge was null or undefined');
    }

    const chartElem = this.$refs['genderDist'] as HTMLCanvasElement;
    const chartConfig: ChartConfiguration<'bar', number[], string> = {
      plugins: [ChartDataLabels, Title, Tooltip] as Plugin<'bar', AnyObject>[],
      type: 'bar',
      data: {
        labels: Object.keys(this.genderDistribution).map(k => {
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
          data: Object.values(this.genderDistribution),
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
}
</script>