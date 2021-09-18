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
  if (typeof responseData === 'string') {
    responseData = JSON.parse(responseData.replace(/\bNaN\b/g, 'null'));
  }
  return responseData;
}


export default class Ajax {
  // eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
  static async post<T>(url: string, data?: any): Promise<Response<T | null>> {
    try {
      const csrfToken = Cookies.get('csrftoken');
      if (!csrfToken) throw new Error("No CSRF token.");
      
      const requestHeaders = {
        'X-CSRFToken': csrfToken,
      };
      const requestConfig = {
        headers: requestHeaders,
        transformRequest: [decamelizeKeys],
        transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys],
      } as AxiosRequestConfig;

      const response = await axios.post<T>(url, data, requestConfig);

      return new Response(response.data, response.status);
    } catch (e) {
      this.createErrorResponse(e);
      throw e;
    }
  }
  
  static async get<T>(url: string): Promise<Response<T | null>> {
    try {
      const requestConfig = {
        transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys],
      } as AxiosRequestConfig;

      const response = await axios.get<T>(url, requestConfig);

      return new Response(response.data, response.status);
    } catch (e) {
      const response = this.createErrorResponse(e);
      if (response == null)
        throw e;
      else
        return response;
    }
  }

  private static createErrorResponse(e: any): Response<null> | null {
    if (e.response) { // Server error
      return new Response(e.response.data, e.response.status);
    }
    else if (e.request) { // Network error
      return new Response(null, e.request.status);
    }
    else { // Client error
      // TODO: handle this error
      return null;
    }
  }
}

/* eslint-enable */

export class Response<T> {
  constructor(public data: T, public statusCode: number) { }

  get isSuccess(): boolean {
    return 200 <= this.statusCode && this.statusCode < 300;
  }
}
