import IdGenerator from "@/util/id-generator";
import { Modal } from "bootstrap";
import { onMounted } from "vue";

export function useModal(emit: { (e: 'onModalHide'): void; (e: 'onModalHidden'): void; }) {
  const modalId = IdGenerator.generateUniqueId('modal');
  let modal: Modal | undefined;
  
  onMounted(() => {
    modal = new Modal(`#${modalId}`);
    modal.show();
  
    const modalElement = document.getElementById(modalId);
    if (modalElement == null) {
      throw new TypeError('Could not find modal element with id ' + modalId);
    }

    modalElement.addEventListener('hide.bs.modal', () => emit('onModalHide'));
    modalElement.addEventListener('hidden.bs.modal', () => emit('onModalHidden'));
  });

  const hideModal = () => {
    modal?.hide();
  };

  return { modalId, hideModal };
}
