import { ResultsType } from "@/util/data";

type CssClass = string | Record<string, boolean> | (string | Record<string, boolean>)[];
type CssStyle = string | Record<string, string | string[]> | (string | Record<string, string | string[]>)[];

export class AnimeTableColumnData {
  constructor(resultType: ResultsType, cssClass: CssClass = {}, cssStyle: CssStyle = {}, width = 10) {
    this.resultType = resultType;
    this.cssClass = cssClass;
    this.cssStyle = cssStyle;
    this.width = width;
  }

  resultType: ResultsType;
  cssClass: CssClass;
  /**
   * Width in percentages. Defaults to 10.
   */
  width: number;

  /**
   * The CSS style rules. Sets the position to relative, text-align to right, and width rules to width by default.
   */
  set cssStyle(value: CssStyle) {
    this._cssStyle = value;
  }
  get cssStyle(): CssStyle {
    const defaultStyle: CssStyle = {
      'position': 'relative',
      'text-align': 'right',
      'width': `${this.width}%!important`,
    };
    return Object.assign(defaultStyle, this._cssStyle ?? {});
  }

  private _cssStyle?: CssStyle;
}