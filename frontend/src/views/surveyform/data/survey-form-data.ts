import type { AnimeViewModel, SurveyViewModel } from "@/util/data";

export interface ResponseData {
  age: number | null;
  gender: string | null;
}

export interface AnimeResponseData {
  animeId: number;
  score?: number;
  watching: boolean;
  underwatched?: boolean;
  expectations?: string;
}

export interface SurveyFormBaseData {
  responseData: ResponseData;
  animeResponseDataDict: Record<number, AnimeResponseData>;
  isResponseLinkedToUser: boolean;
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface SurveyFormSubmitData extends SurveyFormBaseData {}

export interface SurveyFormData extends SurveyFormBaseData {
  survey: SurveyViewModel;
  animeDataDict: Record<number, AnimeViewModel>;
  isAnimeNewDict: Record<number, boolean>;
}