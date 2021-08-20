import axios from 'axios';
import _ from 'lodash';

function camelizeKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(v => camelizeKeys(v));
  } else if (obj != null && obj.constructor === Object) {
    return Object.keys(obj).reduce(
      (result, key) => ({
        ...result,
        [_.camelCase(key)]: camelizeKeys(obj[key]),
      }),
      {},
    );
  }
  return obj;
}

function decamelizeKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(v => decamelizeKeys(v));
  } else if (obj != null && obj.constructor === Object) {
    return Object.keys(obj).reduce(
      (result, key) => ({
        ...result,
        [_.snakeCase(key)]: decamelizeKeys(obj[key]),
      }),
      {},
    );
  }
  return obj;
}

export default class Ajax {
  static async post<T>(url: string, data?: any): Promise<T | null> {
    try {
      const response = await axios.post<T>(url, data);

      // Check if JSON parsing failed
      if (typeof response.data === 'string') {
        // Convert NaNs to nulls
        return <T>JSON.parse(response.data.replace(/\bNaN\b/g, "null"))
      }
      
      return response.data;
    } catch (e) {
      this.handleError(e);
      return null;
    }
  }
  
  static async get<T>(url: string): Promise<T | null> {
    try {
      const response = await axios.get<T>(url);

      // Check if JSON parsing failed
      if (typeof response.data === 'string') {
        // Convert NaNs to nulls
        return <T>JSON.parse(response.data.replace(/\bNaN\b/g, "null"))
      }

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
