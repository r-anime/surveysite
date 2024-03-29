import type { Component } from "vue";

export class ModalService {
  private static eventHandlers: ModalShowFn[] = [];

  /**
   * Show a modal component
   * @param component The modal component.
   * This component **must** implement an `onModalHide` emitter
   * and should handle hiding itself!
   */
  static show(component: Component, initData: ModalInitViewModel = {}): void {
    for (const handler of this.eventHandlers) {
      handler(component, initData);
    }
  }

  static subscribe(func: ModalShowFn): void {
    this.eventHandlers.push(func);
  }

  static unsubscribe(func: ModalShowFn): void {
    this.eventHandlers = this.eventHandlers.filter(handler => handler !== func);
  }
}

export type ModalShowFn = (component: Component, initData: ModalInitViewModel) => void;

export interface ModalInitViewModel {
  data?: unknown;
  emits?: ModalEmits;
}
export interface ModalEmits {
  onModalHide?: () => void;
  onModalHidden?: () => void;
  onModalSuccess?: () => void;
}
