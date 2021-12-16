import { AnimeData, ResultsType } from "@/util/data";

export interface AnimeTableEntryData {
  anime: AnimeData;
  data: Record<ResultsType, number | undefined>;
}