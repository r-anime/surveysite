import axios from 'axios';

export default class Ajax {
  static async post<T>(url: string, data?: any): Promise<T | null> {
    try {
      const response = await axios.post<T>(url, data);
      return response.data;
    } catch (e) {
      this.handleError(e);
      return null;
    }
  }
  static async get<T>(url: string, data?: any): Promise<T | null> {
    try {
      const response = await axios.get<T>(url, data);
      return response.data;
    } catch (e) {
      this.handleError(e);
      return null;
    }
  }

  private static handleError(e: any): void {
    const errorData = new ErrorData();
    errorData.errorString = e.toString();
    if (e.response) {
      errorData.errorType = ErrorType.SERVER;
    }
    else if (e.request) {
      errorData.errorType = ErrorType.NETWORK;
    }
    else {
      errorData.errorType = ErrorType.CLIENT;
    }
    // TODO: Properly handle this error
    console.log(errorData.toString());
  }
}

export enum ErrorType {
  SERVER,
  NETWORK,
  CLIENT,
}

export class ErrorData {
  errorType!: ErrorType;
  errorString!: string;

  toString(): string {
    return `A ${ErrorType[this.errorType].toLowerCase()} error occurred: ${this.errorString}`;
  }
}
