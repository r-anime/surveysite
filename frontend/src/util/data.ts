export type UserViewModel = AuthenticatedUserViewModel | AnonymousUserViewModel;

export interface AuthenticatedUserViewModel {
  authenticated: true;
  username: string;
  profilePictureUrl: string;
  isStaff: boolean;
}

export interface AnonymousUserViewModel {
  authenticated: false;
  authenticationUrl: string;
}

export interface ImageViewModel {
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

export interface AnimeNameViewModel {
  name: string;
  isOfficial: boolean;
  type: AnimeNameType;
}

export interface AnimeViewModel {
  id: number;
  names: AnimeNameViewModel[];
  images: ImageViewModel[];
  animeType: AnimeType;
}

export interface SurveyViewModel {
  year: number;
  season: AnimeSeason;
  isPreseason: boolean;
  openingEpochTime: number;
  closingEpochTime: number;
}

export enum ResultType {
  POPULARITY                  =  1,
  POPULARITY_MALE             =  2,
  POPULARITY_FEMALE           =  3,
  GENDER_POPULARITY_RATIO     =  4,
  SCORE                       = 11,
  SCORE_MALE                  = 12,
  SCORE_FEMALE                = 13,
  GENDER_SCORE_DIFFERENCE     = 14,
  UNDERWATCHED                = 21,
  SURPRISE                    = 22,
  DISAPPOINTMENT              = 23,
  AGE                         = 24,
}

/**
 * Deep-replaces all non-object values of type `T` with `TValue`.
 * 
 * For example, replaces  
 * `{ ab: number; cd: { x: string; z: boolean; } }`  
 * with  
 * `{ ab: TValue; cd: { x: TValue; z: TValue; } }`
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ReplaceAllValues<T, TValue> = T extends Record<string, any> ? {[K in keyof T]: ReplaceAllValues<T[K], TValue>} : TValue;

/**
 * Deep-replaces all non-object values with `string[] | undefined` using {@link ReplaceAllValues}.
 */
export type ValidationErrorData<T> = ReplaceAllValues<T, string[] | undefined>;

export interface SelectorItem {
  id: number;
  name: string;
}

export interface SelectInputOption<T> {
  /** Used to identify the option in the input component, and thus must be unique */
  id: string;
  /** Option value, objects currently not supported */
  value: T extends object ? never : T;
  /** Option name */
  displayName: string;
}
