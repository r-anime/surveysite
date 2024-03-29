import type { UserViewModel } from './data';
import HttpService from './http-service';
import NotificationService from './notification-service';

// Not necessary currently, but might need to use RxJS subscriptions/observables in the future - but using that just for small stuff like this seems overkill for now

export default class UserService {
  static userDataPromise: Promise<UserViewModel | null> = new Promise(resolve => resolve(null));

  static async getUserData(): Promise<UserViewModel | null> {
    const userData = await this.userDataPromise;
    if (!userData) {
      return await this.refreshUserData();
    } else {
      return userData;
    }
  }
  
  static async refreshUserData(): Promise<UserViewModel | null> {
    this.userDataPromise = HttpService.get<UserViewModel, UserViewModel | null>('api/user/', userData => {
      return userData;
    }, errorResponse => {
      NotificationService.pushMsgList(errorResponse.errors?.global ?? ['An unknown error occurred trying to obtain user data'], 'danger');
      return null;
    });

    return await this.userDataPromise;
  }
}