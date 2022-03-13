import { AnimeData, Gender, ResultType, SurveyData } from "@/util/data";

export interface SurveyResultsData {
  results: Record<number, Record<ResultType, number>>;
  anime: Record<number, AnimeData>;
  survey: SurveyData;
  miscellaneous: {
    responseCount: number;
    ageDistribution: Record<number, number>;
    genderDistribution: Record<Gender, number>;
  };
}