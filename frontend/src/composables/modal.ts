import { Modal } from "bootstrap";
import { onMounted } from "vue";

/**
 * Instantiates a Bootstrap Modal component and takes care of events
 * @param emit defineEmits() events
 * @returns Modal data and functionality
 */
export function useModal(
  modalId: string,
  emit: { (e: 'onModalHide'): void; (e: 'onModalHidden'): void; (e: 'onModalSuccess'): void; },
  modalOptions?: Partial<Modal.Options>,
) {
  let modal: Modal | undefined;
  
  onMounted(() => {
    modal = new Modal(`#${modalId}`, modalOptions);
    modal.show();
  
    const modalElement = document.getElementById(modalId);
    if (modalElement == null) {
      throw new TypeError('Could not find modal element with id ' + modalId);
    }

    modalElement.addEventListener('hide.bs.modal', () => emit('onModalHide'));
    modalElement.addEventListener('hidden.bs.modal', () => emit('onModalHidden'));
  });

  const hideModal = (success = false) => {
    if (success) {
      emit('onModalSuccess');
    }
    modal?.hide(); // Triggers onModalHide, and after modal is hidden, onModalHidden
  };

  return {
    /** Hides the modal and triggers onModalHide/onModalHidden, success true also triggers onModalSuccess */
    hideModal,
  };
}
