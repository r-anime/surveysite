<template>
  <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="`${modalId}Label`" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" :id="`${modalId}Label`">{{ modalTitle }}</h5>
          <button class="btn-close" aria-label="Close" @click="onClose"></button>
        </div>
        <div class="modal-body p-4">
          <div class="row row-cols-1">
            <p class="col">
              To edit your response in the future, save the link below. Without this link, you will not be able to edit your response. Do not share it either, as others could then also edit your response.
            </p>
            <div class="col">
              <router-link :to="editLink">
                <!-- Visibility toggle? -->
                {{ editLink }}
              </router-link>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button"
                  class="btn btn-primary"
                  @click="onAccept">
            {{ modalAcceptButtonText }}
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
  (e: 'onModalHide', success: boolean): void;
}>();

const modalId = IdGenerator.generateUniqueId('modal');
const modalTitle = 'Your response was succesfully submitted!';
const modalAcceptButtonText = 'Continue';

const router = useRouter();
const editLink = router.resolve({ name: 'SurveyForm', query: { responseId: props.data } }).fullPath;

let modal: Modal;

nextTick(() => {
  modal = new Modal(`#${modalId}`);
  modal.show();
});


function onClose() {
  modal.hide();
  emit('onModalHide', false);
}

function onAccept() {
  modal.hide();
  emit('onModalHide', true);
}
</script>
