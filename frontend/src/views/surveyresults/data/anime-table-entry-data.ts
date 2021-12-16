import { AnimeData, ResultsType } from "@/util/data";
import _ from "lodash";

export class AnimeTableEntryData {
  anime!: AnimeData;
  data!: {
    resultType: ResultsType,
    value?: number,
  }[];

  getResultValue(resultType: ResultsType): number | undefined {
    return _.find(this.data, datum => datum.resultType === resultType)?.value;
  }
}