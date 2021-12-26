import { AnimeData, SurveyData } from "@/util/data";

export interface ResponseData {
  age?: number;
  gender?: string;
}

export interface AnimeResponseData {
  animeId: number;
  score: number;
  watching: boolean;
  underwatched?: boolean;
  expectations?: string;
}

export interface SurveyFormBaseData {
  responseData: ResponseData;
  animeResponseDataDict: Record<number, AnimeResponseData>;
  isResponseLinkedToUser: boolean;
}

export interface SurveyFormSubmitData extends SurveyFormBaseData {}

export interface SurveyFormData extends SurveyFormBaseData {
  survey: SurveyData;
  animeDataDict: Record<number, AnimeData>;
  isAnimeNewDict: Record<number, boolean>;
}