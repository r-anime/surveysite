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
        <input class="form-control" :id="`input-missinganime-${componentId}-name`" :class="{'is-invalid': validationErrors?.missingAnime?.name}" maxlength="128" type="text" v-model="missingAnimeData.name" :aria-describedby="`input-missinganime-${componentId}-name-errors`">
        <FormValidationErrors :id="`input-missinganime-${componentId}-name-errors`" :validationErrors="validationErrors?.missingAnime?.name"/>
      </div>

      <div class="mb-2">
        <label class="form-label" :for="`input-missinganime-${componentId}-link`">Link to anime:</label>
        <input class="form-control" :id="`input-missinganime-${componentId}-link`" :class="{'is-invalid': validationErrors?.missingAnime?.link}" maxlength="200" type="url" v-model="missingAnimeData.link" :aria-describedby="`input-missinganime-${componentId}-link-errors`">
        <FormValidationErrors :id="`input-missinganime-${componentId}-link-errors`" :validationErrors="validationErrors?.missingAnime?.link"/>
      </div>

      <div class="mb-2">
        <label class="form-label" :for="`input-missinganime-${componentId}-description`">Extra information (optional):</label>
        <textarea class="form-control" :id="`input-missinganime-${componentId}-description`" :class="{'is-invalid': validationErrors?.missingAnime?.description}" rows="3" v-model="missingAnimeData.description" :aria-describedby="`input-missinganime-${componentId}-description-errors`"></textarea>
        <FormValidationErrors :id="`input-missinganime-${componentId}-description-errors`" :validationErrors="validationErrors?.missingAnime?.description"/>
      </div>
    </div>

    <small>
      Anime addition requests will be linked to your account; you will be notified on this site when a request went through or was denied.
    </small>
  </Modal>
</template>

<script lang="ts">
import { Vue, Options } from "vue-class-component";
import Modal from '@/components/Modal.vue';
import NotificationService from "@/util/notification-service";
import { SurveyData, ValidationErrorData } from "@/util/data";
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import { MissingAnimeData } from "../data/missing-anime-data";
import HttpService from "@/util/http-service";

@Options({
  props: {
    missingAnimeData: Object,
    survey: Object,
  },
  components: {
    Modal,
    FormValidationErrors,
  },
})
export default class SurveyFormMissingAnimeModal extends Vue {
  survey!: SurveyData;
  missingAnimeData!: MissingAnimeData;
  validationErrors: ValidationErrorData | null = null;

  private static globalId = 0;
  componentId = `missing-anime-modal-${SurveyFormMissingAnimeModal.globalId++}`;

  async sendMissingAnimeData(): Promise<boolean> {
    const survey = this.survey as SurveyData;
    const preOrPost = survey.isPreseason ? 'pre' : 'post';

    return await HttpService.put(`api/survey/${survey.year}/${survey.season}/${preOrPost}/missinganime/`, this.missingAnimeData, () => {
      NotificationService.push({
        message: `Successfully sent your request to add '${this.missingAnimeData.name}'!`,
        color: 'success',
      });

      this.missingAnimeData.name = '';
      this.missingAnimeData.link = '';
      this.missingAnimeData.description = '';
      this.validationErrors = null;

      return true;
    }, failureResponse => {
      NotificationService.pushMsgList(failureResponse.errors.global ?? [], 'danger');
      
      const validationErrors = failureResponse.errors.validation ?? null;
      if (validationErrors != null) {
        this.validationErrors = validationErrors;
        NotificationService.push({
          message: 'One or more fields are invalid',
          color: 'danger'
        });
      }
      return false;
    });
  }
}
</script>