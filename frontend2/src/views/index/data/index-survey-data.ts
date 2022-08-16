import type { ImageData, ResultType, SurveyData } from '@/util/data';
import type { IndexSurveyAnimeData } from './index-survey-anime-data';

export interface IndexSurveyData extends SurveyData {
  animeResults?: Record<ResultType, IndexSurveyAnimeData[]>; // For finished surveys
  animeImages?: ImageData[];                                  // For upcoming/ongoing suveys
}