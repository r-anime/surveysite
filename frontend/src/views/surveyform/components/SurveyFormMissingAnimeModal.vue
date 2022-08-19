<!-- eslint-disable vue/no-mutating-props -->
<template>
  <Modal modalTitle="Request a missing anime to be added"
         modalButtonClass="p-n2"
         modalButtonVariant="light"
         modalButtonText="Is an anime missing?"
         acceptButtonText="Send"
         :acceptButtonCallback="sendMissingAnimeData">
    <span>
      Note:
    </span>
    <ul>
      <li>Only <b>subbed</b> and <b>widely-available</b> anime from this season will be added to the survey.</li>
      <li>
        OVAs and other irregularly-releasing anime will only be added
        <template v-if="survey.isPreseason">
          to pre-season surveys when they're <b>starting</b>
        </template>
        <template v-else>
          to post-season surveys when they've been <b>fully subbed</b>
        </template>
        this season.
      </li>
      <li>Compilation movies and recaps will <b>not</b> be added unless they <template v-if="survey.isPreseason">will</template> make noticable changes to the original.</li>
    </ul>

    <div>
      <div class="mb-2">
        <label class="form-label" :for="`input-missinganime-${componentId}-name`">Anime name:</label>
        <input class="form-control" :id="`input-missinganime-${componentId}-name`" :class="{'is-invalid': validationErrors?.name}" maxlength="128" type="text" v-model="missingAnimeData.name" :aria-describedby="`input-missinganime-${componentId}-name-errors`">
        <FormValidationErrors :id="`input-missinganime-${componentId}-name-errors`" :validationErrors="validationErrors?.name"/>
      </div>

      <div class="mb-2">
        <label class="form-label" :for="`input-missinganime-${componentId}-link`">Link to anime:</label>
        <input class="form-control" :id="`input-missinganime-${componentId}-link`" :class="{'is-invalid': validationErrors?.link}" maxlength="200" type="url" v-model="missingAnimeData.link" :aria-describedby="`input-missinganime-${componentId}-link-errors`">
        <FormValidationErrors :id="`input-missinganime-${componentId}-link-errors`" :validationErrors="validationErrors?.link"/>
      </div>

      <div class="mb-2">
        <label class="form-label" :for="`input-missinganime-${componentId}-description`">Extra information (optional):</label>
        <textarea class="form-control" :id="`input-missinganime-${componentId}-description`" :class="{'is-invalid': validationErrors?.description}" rows="3" v-model="missingAnimeData.description" :aria-describedby="`input-missinganime-${componentId}-description-errors`"></textarea>
        <FormValidationErrors :id="`input-missinganime-${componentId}-description-errors`" :validationErrors="validationErrors?.description"/>
      </div>
    </div>

    <small>
      Anime addition requests will be linked to your account - you will be notified on this site when a request went through or was denied.
    </small>
  </Modal>
</template>

<script setup lang="ts">
/* eslint-disable vue/no-mutating-props */
import Modal from '@/components/Modal.vue';
import NotificationService from "@/util/notification-service";
import type { NewValidationErrorData, SurveyData } from "@/util/data";
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import type { MissingAnimeData } from "../data/missing-anime-data";
import HttpService from "@/util/http-service";
import IdGenerator from '@/util/id-generator';
import { ref } from 'vue';

const props = defineProps<{
  survey: SurveyData;
  missingAnimeData: MissingAnimeData;
}>();

const validationErrors = ref<NewValidationErrorData<MissingAnimeData> | null>(null);
const componentId = IdGenerator.generateUniqueId('missing-anime-modal-');


function sendMissingAnimeData(): Promise<boolean> {
  const preOrPost = props.survey.isPreseason ? 'pre' : 'post';

  return HttpService.put(`api/survey/${props.survey.year}/${props.survey.season}/${preOrPost}/missinganime/`, props.missingAnimeData, () => {
    NotificationService.push({
      message: `Successfully sent your request to add '${props.missingAnimeData.name}'!`,
      color: 'success',
    });

    props.missingAnimeData.name = '';
    props.missingAnimeData.link = '';
    props.missingAnimeData.description = '';
    validationErrors.value = null;

    return true;
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
    return false;
  });
}
</script>