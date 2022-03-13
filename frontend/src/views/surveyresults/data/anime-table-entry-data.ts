import { AnimeData, ResultType } from "@/util/data";

export interface AnimeTableEntryData {
  anime: AnimeData;
  data: Record<ResultType, number | undefined>;
}