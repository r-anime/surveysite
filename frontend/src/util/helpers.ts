import { AnimeSeason } from "./data";

/**
 * Returns the season's name with the first letter capitalized
 */
export function getSeasonName(season: AnimeSeason): string {
  const seasonNameUpper = AnimeSeason[season];
  return seasonNameUpper.charAt(0) + seasonNameUpper.slice(1).toLowerCase()
}