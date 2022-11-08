import type { ImageViewModel, ResultType, SurveyViewModel } from '@/util/data';
import type { IndexSurveyAnimeData } from './index-survey-anime-data';

export interface IndexSurveyViewModel extends SurveyViewModel {
  animeResults?: Record<ResultType, IndexSurveyAnimeData[]>; // For finished surveys
  animeImages?: ImageViewModel[];                                  // For upcoming/ongoing suveys
}