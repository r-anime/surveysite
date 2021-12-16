import { filter, orderBy } from "lodash";
import { RouteLocation } from "vue-router";
import { AnimeData, AnimeNameType, AnimeSeason, AnimeType, ResultsType } from "./data";

/**
 * Returns the season's name with the first letter capitalized
 * @param season The season
 * @returns The season's name
 */
export function getSeasonName(season: AnimeSeason|number|string): string {
  if (typeof season === 'string') season = Number(season);
  const seasonNameUpper = AnimeSeason[season];
  return seasonNameUpper.charAt(0) + seasonNameUpper.slice(1).toLowerCase()
}

export function getSurveyApiUrl(route: RouteLocation): string {
  const year = route.params['year'];
  const season = route.params['season'];
  const preOrPostSeason = route.params['preOrPost'];
  
  return `api/survey/${year}/${season}/${preOrPostSeason}/`;
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
    anime.animeType == AnimeType.TV_SERIES
}

export function getAnimeName(anime: AnimeData, animeNameType: AnimeNameType): string | null {
  const filtered = filter(anime.names, name => name.type == animeNameType);
  if (!filtered.length) return null;

  const ordered = orderBy(filtered, ['isOfficial', 'name'], ['desc', 'asc']);
  return ordered[0].name;
}

const resultTypeDataMap: Record<ResultsType, { name: string, formatter: (value?: number) => string }> = {
  // Someone please tell me why "hyphens: auto" doesn't work unless I add hyphens manually
  [ResultsType.POPULARITY]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty', formatter: percentageFormatter },
  [ResultsType.POPULARITY_MALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Male)', formatter: percentageFormatter },
  [ResultsType.POPULARITY_FEMALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Fe\u00ADmale)', formatter: percentageFormatter },
  [ResultsType.GENDER_POPULARITY_RATIO]: { name: 'Gen\u00ADder Ra\u00ADtio', formatter: genderRatioFormatter },
  [ResultsType.SCORE]: { name: 'Sco\u00ADre', formatter: numberFormatter },
  [ResultsType.SCORE_MALE]: { name: 'Sco\u00ADre (Male)', formatter: numberFormatter },
  [ResultsType.SCORE_FEMALE]: { name: 'Sco\u00ADre (Female)', formatter: numberFormatter },
  [ResultsType.GENDER_SCORE_DIFFERENCE]: { name: 'Score Diff.', formatter: scoreDiffFormatter },
  [ResultsType.AGE]: { name: 'Avg. Age', formatter: numberFormatter },
  [ResultsType.UNDERWATCHED]: { name: 'Un\u00ADder\u00ADwatch\u00ADed', formatter: percentageFormatter },
  [ResultsType.SURPRISE]: { name: 'Sur\u00ADprise', formatter: percentageFormatter },
  [ResultsType.DISAPPOINTMENT]: { name: 'Dis\u00ADa\u00ADppoint\u00ADment', formatter: percentageFormatter },
};

export function getResultTypeName(resultType: ResultsType, withHyphens = true): string {
  const name = resultTypeDataMap[resultType].name;
  if (!withHyphens) return name.replaceAll('\u00AD', '');
  return name;
}

export function getResultTypeFormatter(resultType: ResultsType): (value?: number) => string {
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
