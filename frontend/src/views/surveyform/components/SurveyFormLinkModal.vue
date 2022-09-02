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
          <div class="row row-cols-1">
            <p class="col">
              To edit your response in the future, save the link below. Without this link, you will not be able to edit your response. Do not share it either, as others could then also edit your response.
            </p>
            <div class="col">
              <RouterLink :to="editRoute">
                <!-- Visibility toggle? -->
                {{ editLink }}
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button"
                  class="btn btn-primary"
                  @click="onSuccess()">
            {{ modalSuccessButtonText }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import IdGenerator from '@/util/id-generator';
import { Modal } from 'bootstrap';
import { nextTick } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  data: string;
}>();

const emit = defineEmits<{
  (e: 'onModalHide'): void;
  (e: 'onModalHidden'): void;
  (e: 'onModalSuccess'): void;
}>();

const modalId = IdGenerator.generateUniqueId('modal');
const modalTitle = 'Your response was succesfully submitted!';
const modalSuccessButtonText = 'Continue';

const router = useRouter();
const editRoute = router.resolve({ name: 'SurveyForm', query: { responseId: props.data }});
const editLink = editRoute.fullPath;


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
function onSuccess() {
  emit('onModalSuccess');
  onHide();
}
</script>
