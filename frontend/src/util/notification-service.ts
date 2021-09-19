import _ from 'lodash';

export default class NotificationService {
  private static eventHandlers: EventHandler[] = [];

  static push(notification: Notification): void {
    for (const handler of this.eventHandlers) {
      handler(notification);
    }
  }

  static pushList(notificationList: Notification[]): void {
    for (const notification of notificationList) {
      this.push(notification);
    }
  }

  static pushMsgList(messageList: string[], color: Color): void {
    for (const message of messageList) {
      this.push({
        message: message,
        color: color,
      });
    }
  }

  static subscribe(func: EventHandler): void {
    this.eventHandlers.push(func);
  }

  static unsubscribe(func: EventHandler): void {
    _.remove(this.eventHandlers, handler => handler == func);
  }
}

type Color = 'primary' | 'secondary' | 'info' | 'success' | 'warning' | 'danger';
type EventHandler = (notification: Notification) => void;

export interface Notification {
  message: string;
  color: Color;
}
