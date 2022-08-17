export default class IdGenerator {
  private static idNumbers: Record<string, number> = {};

  public static generateUniqueId(name: string): string {
    if (IdGenerator.idNumbers[name] != null) {
      IdGenerator.idNumbers[name]++;
    } else {
      IdGenerator.idNumbers[name] = 0;
    }
    return name + IdGenerator.idNumbers[name].toString();
  }
}