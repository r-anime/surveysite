export default class IdGenerator {
  private static idNumbers: Record<string, number> = {};

  /**
   * Generates an id unique among others with the same name
   * @param name Name of the unique id
   * @returns The name with the unique id appended to it
   */
  public static generateUniqueId(name: string): string {
    if (IdGenerator.idNumbers[name] != null) {
      IdGenerator.idNumbers[name]++;
    } else {
      IdGenerator.idNumbers[name] = 0;
    }
    return name + IdGenerator.idNumbers[name].toString();
  }
}