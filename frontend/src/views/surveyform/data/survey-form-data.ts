import { AnimeData, SurveyData } from "@/util/data";

export interface ResponseData {
  age: number | null;
  gender: string | null;
}

export interface AnimeResponseData {
  animeId: number;
  score: number | null;
  watching: boolean;
  underwatched: boolean | null;
  expectations: string | null;
}

export interface SurveyFormBaseData {
  responseData: ResponseData;
  animeResponseDataDict: Record<number, AnimeResponseData>;
  isResponseLinkedToUser: boolean;
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface SurveyFormSubmitData extends SurveyFormBaseData {}

export interface SurveyFormData extends SurveyFormBaseData {
  survey: SurveyData;
  animeDataDict: Record<number, AnimeData>;
  isAnimeNewDict: Record<number, boolean>;
}