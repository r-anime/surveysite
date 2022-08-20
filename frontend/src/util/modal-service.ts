import _ from "lodash";
import type { Component } from "vue";

export class ModalService {
  private static eventHandlers: ((component: Component, onModalHide: (success: boolean) => void, data?: unknown) => void)[] = [];

  /**
   * Show a modal component
   * @param component The modal component.
   * This component **must** implement an `onModalHide` emitter
   * and should handle hiding itself!
   */
  static show(component: Component, onModalHide: (success: boolean) => void = () => { return; }, data?: unknown): void {
    for (const handler of this.eventHandlers) {
      handler(component, onModalHide, data);
    }
  }

  static subscribe(func: (component: Component, onModalHide: (success: boolean) => void, data?: unknown) => void): void {
    this.eventHandlers.push(func);
  }

  static unsubscribe(func: (component: Component, onModalHide: (success: boolean) => void, data?: unknown) => void): void {
    _.remove(this.eventHandlers, handler => handler == func);
  }
}
