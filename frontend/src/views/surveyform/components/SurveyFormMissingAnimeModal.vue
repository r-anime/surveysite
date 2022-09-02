<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="`${modalId}Label`" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">

        <div class="modal-header">
          <h5 class="modal-title" :id="`${modalId}Label`">{{ modalTitle }}</h5>
          <button class="btn-close"
                  aria-label="Close"
                  @click="onHide">
          </button>
        </div>

        <div class="modal-body p-4">
          <span>
            Note:
          </span>
          <ul>
            <li>Only <b>subbed</b> and <b>widely-available</b> anime from this season will be added to the survey.</li>
            <li>
              OVAs and other irregularly-releasing anime will only be added
              <template v-if="data.survey.isPreseason">
                to pre-season surveys when they're <b>starting</b>
              </template>
              <template v-else>
                to post-season surveys when they've been <b>fully subbed</b>
              </template>
              this season.
            </li>
            <li>Compilation movies and recaps will <b>not</b> be added unless they <template v-if="data.survey.isPreseason">will</template> make noticable changes to the original.</li>
          </ul>

          <div>
            <div class="mb-2">
              <label class="form-label" :for="`input-missinganime-${modalId}-name`">Anime name:</label>
              <input class="form-control" :id="`input-missinganime-${modalId}-name`" :class="{'is-invalid': validationErrors?.name}" maxlength="128" type="text" v-model="data.missingAnimeData.name" :aria-describedby="`input-missinganime-${modalId}-name-errors`">
              <FormValidationErrors :id="`input-missinganime-${modalId}-name-errors`" :validationErrors="validationErrors?.name"/>
            </div>

            <div class="mb-2">
              <label class="form-label" :for="`input-missinganime-${modalId}-link`">Link to anime:</label>
              <input class="form-control" :id="`input-missinganime-${modalId}-link`" :class="{'is-invalid': validationErrors?.link}" maxlength="200" type="url" v-model="data.missingAnimeData.link" :aria-describedby="`input-missinganime-${modalId}-link-errors`">
              <FormValidationErrors :id="`input-missinganime-${modalId}-link-errors`" :validationErrors="validationErrors?.link"/>
            </div>

            <div class="mb-2">
              <label class="form-label" :for="`input-missinganime-${modalId}-description`">Extra information (optional):</label>
              <textarea class="form-control" :id="`input-missinganime-${modalId}-description`" :class="{'is-invalid': validationErrors?.description}" rows="3" v-model="data.missingAnimeData.description" :aria-describedby="`input-missinganime-${modalId}-description-errors`"></textarea>
              <FormValidationErrors :id="`input-missinganime-${modalId}-description-errors`" :validationErrors="validationErrors?.description"/>
            </div>
          </div>

          <small>
            Anime addition requests will be linked to your account - you will be notified on this site when a request went through or was denied.
          </small>
        </div>

        <div class="modal-footer">
          <button type="button"
                  class="btn btn-secondary"
                  @click="onHide">
            Cancel
          </button>

          <button type="button"
                  class="btn btn-primary"
                  @click="onSuccess">
            {{ acceptButtonText }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* eslint-disable vue/no-mutating-props */
import NotificationService from "@/util/notification-service";
import type { ValidationErrorData, SurveyData } from "@/util/data";
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import type { MissingAnimeData } from "../data/missing-anime-data";
import HttpService from "@/util/http-service";
import IdGenerator from '@/util/id-generator';
import { nextTick, ref } from 'vue';
import { Modal } from "bootstrap";

const props = defineProps<{
  data: {
    survey: SurveyData;
    missingAnimeData: MissingAnimeData;
  };
}>();

const emit = defineEmits<{
  (e: 'onModalHide'): void;
  (e: 'onModalHidden'): void;
  (e: 'onModalSuccess'): void;
}>();

const validationErrors = ref<ValidationErrorData<MissingAnimeData> | null>(null);
const modalId = IdGenerator.generateUniqueId('missingAnimeModal');
const modalTitle = 'Request a missing anime to be added';
const acceptButtonText = 'Send';

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
  const preOrPost = props.data.survey.isPreseason ? 'pre' : 'post';

  HttpService.put(`api/survey/${props.data.survey.year}/${props.data.survey.season}/${preOrPost}/missinganime/`, props.data.missingAnimeData, () => {
    NotificationService.push({
      message: `Successfully sent your request to add '${props.data.missingAnimeData.name}'!`,
      color: 'success',
    });

    props.data.missingAnimeData.name = '';
    props.data.missingAnimeData.link = '';
    props.data.missingAnimeData.description = '';
    validationErrors.value = null;

    onHide();
  }, failureResponse => {
    NotificationService.pushMsgList(failureResponse.errors?.global ?? (failureResponse.status === 404 ? ['Survey not found!'] : []), 'danger');
    
    const validationErrorsTemp = failureResponse.errors?.validation ?? null;
    if (validationErrorsTemp != null) {
      validationErrors.value = validationErrorsTemp;
      NotificationService.push({
        message: 'One or more fields are invalid',
        color: 'danger'
      });
    }
  });
}
</script>