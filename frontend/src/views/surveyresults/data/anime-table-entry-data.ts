import type { AnimeViewModel, ResultType } from "@/util/data";

export interface AnimeTableEntryData {
  anime: AnimeViewModel;
  data: Record<ResultType, number | undefined>;
}