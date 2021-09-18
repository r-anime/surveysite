import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
import Cookies from 'js-cookie';
import _ from 'lodash';
/* eslint-disable @typescript-eslint/no-explicit-any */

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


function getResponseData<T>(response: AxiosResponse<any>): Response<T | null> {
  if (!response.data) return new Response(null, response.status);
  let responseData;

  // Check if JSON parsing failed
  if (typeof response.data === 'string') {
    // Convert NaNs to nulls
    responseData = JSON.parse(response.data.replace(/\bNaN\b/g, 'null'))
  }
  else {
    responseData = response.data;
  }

  return new Response(camelizeKeys(responseData) as T, response.status);
}

function convertRequestData(data?: any): any {
  return decamelizeKeys(data);
}


export default class Ajax {
  // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
  static async post<T>(url: string, data?: any): Promise<Response<T | null>> {
    try {
      const csrfToken = Cookies.get('csrftoken');
      if (!csrfToken) throw new Error("No CSRF token");
      
      const requestHeaders = {
        'X-CSRFToken': csrfToken,
      };
      const requestConfig = {
        headers: requestHeaders,
        validateStatus: status => true,
      } as AxiosRequestConfig;

      const response = await axios.post<T>(url, convertRequestData(data), requestConfig);

      return getResponseData<T>(response);
    } catch (e) {
      this.handleError(e);
      throw e;
    }
  }
  
  static async get<T>(url: string): Promise<Response<T | null>> {
    try {
      const response = await axios.get<T>(url);
      return getResponseData<T>(response);
    } catch (e) {
      this.handleError(e);
      throw e;
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
    console.log(e);
  }
}

/* eslint-enable */

export class Response<T> {
  constructor(public data: T, public statusCode: number) { }

  get isSuccess(): boolean {
    return 200 <= this.statusCode && this.statusCode < 300;
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
