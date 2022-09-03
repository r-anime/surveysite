<!-- eslint-disable vue/no-mutating-props -->
<template>
  <ModalTemplate :modalId="modalId"
                 :modalHeaderText="modalTitle"
                 :modalFooterSuccessButtonText="acceptButtonText"
                 @onHide="onHide"
                 @onSuccess="onSuccess">

    <template #body>
      <span>Note:</span>
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
    </template>

  </ModalTemplate>
</template>

<script setup lang="ts">
/* eslint-disable vue/no-mutating-props */
import NotificationService from "@/util/notification-service";
import type { ValidationErrorData, SurveyData } from "@/util/data";
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import type { MissingAnimeData } from "../data/missing-anime-data";
import HttpService from "@/util/http-service";
import { ref } from 'vue';
import ModalTemplate from '@/components/ModalTemplate.vue';
import { useModal } from "@/composables/modal";

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

const { modalId, hideModal } = useModal(emit);

const validationErrors = ref<ValidationErrorData<MissingAnimeData> | null>(null);
const modalTitle = 'Request a missing anime to be added';
const acceptButtonText = 'Send';

function onHide() {
  hideModal();
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

    hideModal();
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