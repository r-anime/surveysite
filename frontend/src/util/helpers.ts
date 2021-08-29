import { AnimeSeason, SurveyData } from "./data";

/**
 * Returns the season's name with the first letter capitalized
 * @param season The season
 * @returns The season's name
 */
export function getSeasonName(season: AnimeSeason): string {
  const seasonNameUpper = AnimeSeason[season];
  return seasonNameUpper.charAt(0) + seasonNameUpper.slice(1).toLowerCase()
}

/**
 * Gets the survey's name with proper title capitalization
 * @param survey The survey
 * @returns The survey's name
 */
export function getSurveyName(survey: SurveyData): string {
  return `The ${survey.isPreseason ? 'Start' : 'End'} of ${getSeasonName(survey.season)} ${survey.year} Survey`;
}
