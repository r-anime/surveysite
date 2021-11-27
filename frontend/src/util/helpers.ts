import { filter, orderBy } from "lodash";
import { RouteLocation } from "vue-router";
import { AnimeData, AnimeNameType, AnimeSeason, AnimeType, SurveyData } from "./data";

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
 * @param survey The survey
 * @returns The survey's name
 */
export function getSurveyName(survey: SurveyData): string {
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
