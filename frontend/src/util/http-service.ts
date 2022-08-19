import axios from "axios";
import type { AxiosRequestConfig, AxiosResponse } from "axios";
import Cookies from "js-cookie";
import _ from "lodash";
import type { NewValidationErrorData } from "./data";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
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


// eslint-disable-next-line @typescript-eslint/no-explicit-any
function fixResponseDataIfJsonParsingFailed(responseData: any) {
  if (!responseData) {
    // Response data is null
    return responseData;
  } else if (typeof responseData === 'string') {
    try {
      // Try to parse the response after replacing NaNs with nulls
      return JSON.parse(responseData.replace(/\bNaN\b/g, 'null'));
    } catch (e) {
      return {};
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

export default class HttpService {
  private static _axios = axios.create({
    transformRequest: [decamelizeKeys, data => JSON.stringify(data)], // TODO: Perform decamelizing on backend
    transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys], // TODO: Perform camelizing on backend and send nulls instead of NaNs
    baseURL: '/',
    validateStatus: statusCode => (statusCode >= 200 && statusCode < 300) || (statusCode >= 400 && statusCode < 500),
  });

  static async get<TResponse, TResult = void>(url: string, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<never>) => TResult): Promise<TResult> {
    return await this.performRequestFn(this._axios.get, url, successFn, failureFn);
  }

  static async post<TResponse, TRequest, TResult = void>(url: string, data: TRequest, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<TRequest>) => TResult): Promise<TResult> {
    return await this.performDataRequestFn(this._axios.post, url, data, successFn, failureFn);
  }

  static async put<TResponse, TRequest, TResult = void>(url: string, data: TRequest, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<TRequest>) => TResult): Promise<TResult> {
    return await this.performDataRequestFn(this._axios.put, url, data, successFn, failureFn);
  }

  static async delete<TResponse, TRequest, TResult = void>(url: string, data: TRequest, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<TRequest>) => TResult): Promise<TResult> {
    return await this.performDataRequestFn(this._axios.delete, url, data, successFn, failureFn);
  }


  private static async performRequestFn<TResponse, TResult>(axiosRequestFn: AxiosRequestFn<TResponse | ErrorResponse<never>>, url: string, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<never>) => TResult): Promise<TResult> {
    const response = await axiosRequestFn(url);
    return this.processResponse(response, successFn, failureFn);
  }

  private static async performDataRequestFn<TResponse, TRequest, TResult>(axiosDataRequestFn: AxiosDataRequestFn<TResponse | ErrorResponse<TRequest>, TRequest>, url: string, data: TRequest, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<TRequest>) => TResult): Promise<TResult> {
    const config: AxiosRequestConfig = {
      headers: {
        'X-CSRFToken': this.getCsrfToken(),
      },
    };
    const response = await axiosDataRequestFn(url, data, config);

    return this.processResponse(response, successFn, failureFn);
  }


  private static processResponse<TResponse, TRequest, TResult>(response: AxiosResponse<TResponse | ErrorResponse<TRequest>>, successFn: (response: TResponse) => TResult, failureFn?: (response: ErrorResult<TRequest>) => TResult): TResult {
    if (this.isResponseSuccess(response)) {
      return successFn(response.data);
    } else if (response.status === 401) { // Make sure the user is authenticated before performing this request!
      throw new Error('User unauthenticated');
    } else if (this.isResponseValidationErrorData(response)) {
      if (failureFn) {
        const errorResult: ErrorResult<TRequest> = Object.assign({ status: response.status }, response.data);
        return failureFn(errorResult);
      } else {
        throw new Error('The server responded with an error status, but no failure handler was given.');
      }
    } else {
      throw new Error('The server responded with invalid data.');
    }
  }


  private static isResponseSuccess<TResponse, TRequest>(response: AxiosResponse<TResponse | ErrorResponse<TRequest>>): response is AxiosResponse<TResponse> {
    return response.status >= 200 && response.status < 300;
  }

  private static isResponseValidationErrorData<TResponse, TRequest>(response: AxiosResponse<TResponse | ErrorResponse<TRequest>>): response is AxiosResponse<ErrorResponse<TRequest>> {
    return response.status >= 400 && response.status < 600;
  }


  private static getCsrfToken(): string {
    const csrfToken = Cookies.get('csrftoken');
    if (!csrfToken) throw new Error("No CSRF token.");
    return csrfToken;
  }
}

type AxiosRequestFn<TResponse> = (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<TResponse>>;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AxiosDataRequestFn<TResponse, TRequest> = (url: string, data?: TRequest, config?: AxiosRequestConfig) => Promise<AxiosResponse<TResponse>>;

type ErrorResponse<T> = {
  errors?: {
    global?: string[],
    validation?: T extends never ? never : NewValidationErrorData<T>,
  },
};

type ErrorResult<T> = {
  errors?: {
    global?: string[],
    validation?: T extends never ? never : NewValidationErrorData<T>,
  },
  status: number,
}
