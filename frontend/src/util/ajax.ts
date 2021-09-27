import axios, { AxiosRequestConfig, AxiosError, AxiosResponse } from 'axios';
import Cookies from 'js-cookie';
import _ from 'lodash';

/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types */

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
    // Response data is null
    return responseData;
  } else if (typeof responseData === 'string') {
    try {
      // Try to parse the response after replacing NaNs with nulls
      return JSON.parse(responseData.replace(/\bNaN\b/g, 'null'));
    } catch (e) {
      // The response was not JSON
      if (e instanceof SyntaxError) {
        throw new Error('The server returned an invalid response');
      } else {
        throw e;
      }
    }
  } else {
    return responseData;
  }
}

export default class Ajax {
  private static _axios = axios.create({
    transformRequest: [decamelizeKeys, JSON.stringify],
    transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys],
    baseURL: '/',
  });
  
  
  static async get<T>(url: string): Promise<Response<T | ErrorData>> {
    return await Ajax.performRequestFn(Ajax._axios.get, url);
  }

  static async post<T>(url: string, data?: any): Promise<Response<T | ErrorData>> {
    return await Ajax.performRequestFnWithData(Ajax._axios.post, url, data);
  }

  static async put<T>(url: string, data?: any): Promise<Response<T | ErrorData>> {
    return await Ajax.performRequestFnWithData(Ajax._axios.put, url, data);
  }


  private static async performRequestFn<T>(axiosFn: AxiosRequestFn<T>, url: string): Promise<Response<T | ErrorData>> {
    try {
      const response = await axiosFn(url);
      return new Response(response.data, response.status);
    } catch (e) {
      return Response.createErrorResponse(e as AxiosError);
    }
  }

  private static async performRequestFnWithData<T>(axiosFn: AxiosRequestFnWithData<T>, url: string, data?: any): Promise<Response<T | ErrorData>> {
    try {
      const requestConfig = {
        headers: {
          'X-CSRFToken': Ajax.getCsrfToken(),
        },
      } as AxiosRequestConfig;

      const response = await axiosFn(url, data, requestConfig);
      return new Response(response.data, response.status);
    } catch (e) {
      return Response.createErrorResponse(e as AxiosError);
    }
  }

  private static getCsrfToken(): string {
    const csrfToken = Cookies.get('csrftoken');
    if (!csrfToken) throw new Error("No CSRF token.");
    return csrfToken;
  }
}

type AxiosRequestFn<T> = (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
type AxiosRequestFnWithData<T> = (url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;


export class Response<T> {
  constructor(public data: T, public statusCode: number) {}

  getGlobalErrors(unknownError: string | null = 'An unknown error occurred.'): string[] {
    if (Response.isErrorData(this.data)) {
      return this.data.errors.global ?? (unknownError ? [unknownError] : []);
    } else {
      return [];
    }
  }

  static isErrorData(responseData: any): responseData is ErrorData {
    if (typeof responseData === 'string') return false;
    return 'errors' in (responseData ?? {});
  }
  
  static createErrorResponse(e: AxiosError<ErrorData>): Response<ErrorData> {
    if (e.response) {
      // Server error, data returned by server should always be ErrorData so double-check
      if (Response.isErrorData(e.response.data)) {
        return new Response(e.response.data, e.response.status);
      } else {
        throw e;
      }
    }
    else if (e.request) {
      // Network error
      const request: XMLHttpRequest = e.request;
      const errorData: ErrorData = { errors: {
        global: [`While sending a request, an Http${request.status} was encountered.`]
      }};
      return new Response(errorData, request.status);
    }
    else {
      // Client error, return error response with custom status code
      const errorData: ErrorData = { errors: {
        global: [`${e.name}: ${e.message}`]
      }};
      return new Response(errorData, 999);
    }
  }
}

export interface ErrorData {
  errors: {
    global: string[],
    validation?: Record<string, any>,
  };
}

/* eslint-enable */
