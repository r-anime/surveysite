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

export interface AnimeNameData {
  name: string;
  isOfficial: boolean;
  type: AnimeNameType;
}

export interface AnimeData {
  names: AnimeNameData[];
  images: ImageData[];
}
