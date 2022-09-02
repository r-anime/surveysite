<template>
  <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="`${modalId}Label`" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">

        <div class="modal-header">
          <h5 class="modal-title" :id="`${modalId}Label`">{{ modalTitle }}</h5>
          <button class="btn-close"
                  aria-label="Close"
                  @click="onHide()">
          </button>
        </div>

        <div class="modal-body p-4">
          To fill in surveys, you must be logged in with a Reddit account.
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>

          <form v-if="userData" method="POST" :action="userData.authenticationUrl">
            <input type="hidden" name="csrfmiddlewaretoken" :value="getCsrfToken()">
            <button type="submit" class="btn btn-primary">{{ acceptButtonText }}</button>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import IdGenerator from '@/util/id-generator';
import Cookie from 'js-cookie';
import { Modal } from 'bootstrap';
import { nextTick, ref } from 'vue';
import UserService from '@/util/user-service';
import type { AnonymousUserData } from '@/util/data';

defineProps<{
  data: unknown;
}>();

const emit = defineEmits<{
  (e: 'onModalHide'): void;
  (e: 'onModalHidden'): void;
  (e: 'onModalSuccess'): void;
}>();

const modalId = IdGenerator.generateUniqueId('modal');
const modalTitle = 'Log In';
const acceptButtonText = 'Log in via Reddit';
const userData = ref<AnonymousUserData | null>(null);

UserService.getUserData().then(ud => {
  if (ud?.authenticated) {
    onHide();
  } else {
    userData.value = ud;
  }
});

let modal: Modal;

nextTick(() => {
  modal = new Modal(`#${modalId}`);
  modal.show();

  const modalElement = document.getElementById(modalId);
  if (modalElement == null) {
    throw new TypeError('Could not find modal element with id ' + modalId);
  }
  modalElement.addEventListener('hide.bs.modal', () => emit('onModalHide'));
  modalElement.addEventListener('hidden.bs.modal', () => emit('onModalHidden'));
});

function onHide() {
  modal.hide();
}
function getCsrfToken(): string | undefined {
  return Cookie.get('csrftoken');
}
</script>
