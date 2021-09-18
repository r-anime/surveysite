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


function fixResponseDataIfJsonParsingFailed(responseData: any) {
  if (!responseData) {
    return responseData;
  } else if (typeof responseData === 'string') {
    return JSON.parse(responseData.replace(/\bNaN\b/g, 'null'));
  } else {
    return responseData;
  }
}

export default class Ajax {
  // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
  static async post<T>(url: string, data?: any): Promise<Response<T | ErrorData>> {
    try {
      const csrfToken = Cookies.get('csrftoken');
      if (!csrfToken) throw new Error("No CSRF token.");
      
      const requestHeaders = {
        'X-CSRFToken': csrfToken,
      };
      const requestConfig = {
        headers: requestHeaders,
        transformRequest: [decamelizeKeys, JSON.stringify],
        transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys],
      } as AxiosRequestConfig;

      const response = await axios.post<T>(url, data, requestConfig);

      return new Response(response.data, response.status);
    } catch (e) {
      const response = this.createErrorResponse<T>(e);
      if (response == null) {
        throw e;
      } else {
        return response;
      }
    }
  }
  
  static async get<T>(url: string): Promise<Response<T | ErrorData>> {
    try {
      const requestConfig = {
        transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys],
      } as AxiosRequestConfig;

      const response = await axios.get<T>(url, requestConfig);

      return new Response(response.data, response.status);
    } catch (e) {
      const response = this.createErrorResponse<T>(e);
      if (response == null) {
        throw e;
      } else {
        return response;
      }
    }
  }

  private static createErrorResponse<T>(e: any): Response<T | ErrorData> | null {
    if (e.response) { // Server error
      return new Response(e.response.data, e.response.status);
    }
    else if (e.request) { // Network error
      return Response.createNetworkErrorResponse(e.request.status);
    }
    else { // Client error
      return Response.createClientErrorResponse(e);
    }
  }
}

/* eslint-enable */

export class Response<T> {
  constructor(public data: T, public statusCode: number) { }

  static isErrorData(responseData: any): responseData is ErrorData {
    return 'errors' in responseData;
  }

  getGlobalErrors(unknownError: string | null = 'An unknown error occurred.'): string[] {
    // Not pretty but works
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return (this.data as any)?.errors?.global ?? (unknownError ? [unknownError] : []);
  }

  static createClientErrorResponse(error: Error): Response<ErrorData> {
    return new Response({errors: {global: [`${error.name}: ${error.message}`]}} as ErrorData, 999);
  }

  static createNetworkErrorResponse(statusCode: number): Response<ErrorData> {
    return new Response({errors: {global: [`While sending a request, an Http${statusCode} was encountered.`]}} as ErrorData, statusCode);
  }
}

export interface ErrorData {
  isError: true;
  errors: {global: string[]};
}
