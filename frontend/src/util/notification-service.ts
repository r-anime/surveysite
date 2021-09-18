import _ from 'lodash';

export default class NotificationService {
  private static eventHandlers: EventHandler[] = [];

  static push(notification: Notification): void {
    console.log('pushed:');
    console.log(notification);
    for (let handler of this.eventHandlers) {
      handler(notification);
      console.log('to a handler');
    }
  }

  static subscribe(func: EventHandler): void {
    console.log('subscribed a function');
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
