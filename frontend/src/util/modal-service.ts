import _ from "lodash";
import type { Component } from "vue";

export class ModalService {
  private static eventHandlers: ((component: Component, onModalHide: () => void) => void)[] = [];

  /**
   * Show a modal component
   * @param component The modal component.
   * This component **must** implement an `onModalHide` emitter
   * and should handle hiding itself!
   */
  static show(component: Component, onModalHide: () => void = () => { return; }): void {
    for (const handler of this.eventHandlers) {
      handler(component, onModalHide);
    }
  }

  static subscribe(func: (component: Component, onModalHide: () => void) => void): void {
    this.eventHandlers.push(func);
  }

  static unsubscribe(func: (component: Component, onModalHide: () => void) => void): void {
    _.remove(this.eventHandlers, handler => handler == func);
  }
}
