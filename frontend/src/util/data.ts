export interface UserData {
  authenticated: boolean;
  username?: string;
  profilePicture?: string;
}

export interface ImageData {
  name: string;
  urlSmall: string;
  urlMedium: string;
  urlLarge: string;
}

export enum AnimeNameType {
  JAPANESE_NAME = 'JP',
  ENGLISH_NAME  = 'EN',
  SHORT_NAME    = 'SH',
}

export enum AnimeSeason {
  WINTER = 0,
  SPRING = 1,
  SUMMER = 2,
  FALL   = 3,
}

export interface AnimeNameData {
  name: string;
  isOfficial: boolean;
  type: AnimeNameType;
}

export interface AnimeData {
  names: AnimeNameData[];
  images: ImageData[];
}

export interface SurveyAnimeData {
    anime: AnimeData;
    result: number;
}

export interface SurveyData {
    year: number;
    season: AnimeSeason;
    isPreseason: boolean;
    openingEpochTime: number;
    closingEpochTime: number;
    mostPopularAnime: SurveyAnimeData[];
    bestAnime: SurveyAnimeData[];
}
