<template>
  <ModalTemplate :modalId="modalId"
                 :modalHeaderText="modalTitle"
                 @onHide="onHide"
                 @onSuccess="onSuccess">

    <template #body>
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
    </template>

    <template #footer>
      <button type="button"
              class="btn btn-primary"
              @click="onSuccess()">
        {{ modalSuccessButtonText }}
      </button>
    </template>
    
  </ModalTemplate>
</template>

<script setup lang="ts">
import IdGenerator from '@/util/id-generator';
import { Modal } from 'bootstrap';
import { nextTick } from 'vue';
import { useRouter } from 'vue-router';
import ModalTemplate from '@/components/ModalTemplate.vue';

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
