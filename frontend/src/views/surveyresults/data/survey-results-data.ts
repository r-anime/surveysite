import type { AnimeViewModel, Gender, ResultType, SurveyViewModel } from "@/util/data";

export interface SurveyResultsData {
  results: Record<number, Record<ResultType, number>>;
  anime: Record<number, AnimeViewModel>;
  survey: SurveyViewModel;
  miscellaneous: {
    responseCount: number;
    ageDistribution: Record<number, number>;
    genderDistribution: Record<Gender, number>;
  };
}