import { filter, orderBy } from "lodash";
import type { RouteLocation } from "vue-router";
import { type AnimeData, AnimeNameType, AnimeSeason, AnimeType, ResultType } from "./data";

/**
 * Returns the season's name with the first letter capitalized
 * @param season The season
 * @returns The season's name
 */
export function getSeasonName(season: AnimeSeason|number|string): string {
  if (typeof season === 'string') season = Number(season);
  const seasonNameUpper = AnimeSeason[season];
  return seasonNameUpper.charAt(0) + seasonNameUpper.slice(1).toLowerCase();
}

export function getSurveyApiUrl(route: RouteLocation): string {
  const year = route.params['year'];
  const season = route.params['season'];
  const preOrPostSeason = route.params['preOrPost'];
  
  return `api/survey/${year}/${season}/${preOrPostSeason}/`;
}

/**
 * Gets the survey's name from the survey specified in the route.  
 * Handing an invalid survey route may lead to unexpected results as no checks are performed!
 */
export function getSurveyNameFromRoute(route: RouteLocation): string {
  return getSurveyName({
    isPreseason: route.params['preOrPost'] !== 'post', // Pre-season as fallback
    season: Number(route.params['season']),
    year: Number(route.params['year']),
  });
}

/**
 * Gets the survey's name with proper title capitalization
 * @param survey The survey data
 * @returns The survey's name, e.g. 'The End of Fall 2021 Survey'
 */
export function getSurveyName(survey: { isPreseason: boolean, season: AnimeSeason, year: number }): string {
  return `The ${survey.isPreseason ? 'Start' : 'End'} of ${getSeasonName(survey.season)} ${survey.year} Survey`;
}

export function isAnimeSeries(anime: AnimeData): boolean {
  return anime.animeType == AnimeType.BULK_RELEASE ||
    anime.animeType == AnimeType.ONA_SERIES ||
    anime.animeType == AnimeType.TV_SERIES;
}

export function getAnimeName(anime: AnimeData, animeNameType: AnimeNameType): string | null {
  const filtered = filter(anime.names, name => name.type == animeNameType);
  if (!filtered.length) return null;

  const ordered = orderBy(filtered, ['isOfficial', 'name'], ['desc', 'asc']);
  return ordered[0].name;
}

const resultTypeDataMap: Record<ResultType, { name: string, formatter: (value?: number) => string }> = {
  // Someone please tell me why "hyphens: auto" doesn't work unless I add hyphens manually
  [ResultType.POPULARITY]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty', formatter: percentageFormatter },
  [ResultType.POPULARITY_MALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Male)', formatter: percentageFormatter },
  [ResultType.POPULARITY_FEMALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Fe\u00ADmale)', formatter: percentageFormatter },
  [ResultType.GENDER_POPULARITY_RATIO]: { name: 'Gen\u00ADder Ra\u00ADtio', formatter: genderRatioFormatter },
  [ResultType.SCORE]: { name: 'Sco\u00ADre', formatter: numberFormatter },
  [ResultType.SCORE_MALE]: { name: 'Sco\u00ADre (Male)', formatter: numberFormatter },
  [ResultType.SCORE_FEMALE]: { name: 'Sco\u00ADre (Fe\u00ADmale)', formatter: numberFormatter },
  [ResultType.GENDER_SCORE_DIFFERENCE]: { name: 'Score Diff.', formatter: scoreDiffFormatter },
  [ResultType.AGE]: { name: 'A\u00ADve\u00ADrage Age', formatter: numberFormatter },
  [ResultType.UNDERWATCHED]: { name: 'Un\u00ADder\u00ADwatch\u00ADed', formatter: percentageFormatter },
  [ResultType.SURPRISE]: { name: 'Sur\u00ADprise', formatter: percentageFormatter },
  [ResultType.DISAPPOINTMENT]: { name: 'Dis\u00ADa\u00ADppoint\u00ADment', formatter: percentageFormatter },
};

export function getResultTypeName(resultType: ResultType, withHyphens = true): string {
  const name = resultTypeDataMap[resultType].name;
  if (!withHyphens) return name.replace('\u00AD', '');
  return name;
}

export function getResultTypeFormatter(resultType: ResultType): (value?: number) => string {
  return resultTypeDataMap[resultType].formatter;
}

const invalidValue = 'N/A';

function percentageFormatter(value?: number): string {
  if (!value) return invalidValue;
  return (value * 100).toFixed(1) + '%';
}

function genderRatioFormatter(value?: number): string {
  if (!value) return invalidValue;

  const shouldInvert = value < 1;
  if (shouldInvert && value === 0) return invalidValue;
  return (shouldInvert ? 1 / value : value).toFixed(2) + ' ' + (shouldInvert ? 'F:M' : 'M:F');
}

function numberFormatter(value?: number): string {
  if (!value) return invalidValue;
  return value.toFixed(2);
}

function scoreDiffFormatter(value?: number): string {
  if (!value) return invalidValue;

  const shouldInvert = value < 0;
  return (shouldInvert ? -value : value).toFixed(2) + ' ' + (shouldInvert ? 'F' : 'M');
}
