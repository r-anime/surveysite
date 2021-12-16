export interface UserData {
  authenticated: boolean;
  username?: string;
  profilePicture?: string;
  authenticationUrl?: string;
}

export interface ImageData {
  name: string;
  urlSmall: string;
  urlMedium: string;
  urlLarge: string;
}

export enum Gender {
  MALE = 'M',
  FEMALE = 'F',
  OTHER = 'O',
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

export enum AnimeType {
  TV_SERIES    = 'TV',
  ONA_SERIES   = 'ONAS',
  BULK_RELEASE = 'BULK',
  MOVIE        = 'MV',
  ONA          = 'ONA',
  OVA          = 'OVA',
  TV_SPECIAL   = 'TVSP',
}

export interface AnimeNameData {
  name: string;
  isOfficial: boolean;
  type: AnimeNameType;
}

export interface AnimeData {
  id: number;
  names: AnimeNameData[];
  images: ImageData[];
  animeType: AnimeType;
}

export interface SurveyData {
  year: number;
  season: AnimeSeason;
  isPreseason: boolean;
  openingEpochTime: number;
  closingEpochTime: number;
}

export enum ResultsType {
    POPULARITY                  =  1,
    POPULARITY_MALE             =  2,
    POPULARITY_FEMALE           =  3,
    GENDER_POPULARITY_RATIO     =  4,
    //GENDER_POPULARITY_RATIO_INV =  5, // Should preferably not be used
    SCORE                       = 11,
    SCORE_MALE                  = 12,
    SCORE_FEMALE                = 13,
    GENDER_SCORE_DIFFERENCE     = 14,
    //GENDER_SCORE_DIFFERENCE_INV = 15, // Should preferably not be used
    UNDERWATCHED                = 21,
    SURPRISE                    = 22,
    DISAPPOINTMENT              = 23,
    AGE                         = 24,
}
