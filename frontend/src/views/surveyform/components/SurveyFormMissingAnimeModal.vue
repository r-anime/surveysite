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
        <template v-if="isSurveyPreseason">
          to pre-season surveys when they're <b>starting</b>
        </template>
        <template v-else>
          to post-season surveys when they've been <b>fully subbed</b>
        </template>
        this season.
      </li>
      <li>Compilation movies and recaps will <b>not</b> be added unless they <template v-if="isSurveyPreseason">will</template> make noticable changes to the original.</li>
    </ul>

    <div>
      <div class="mb-2">
        <label class="form-label" :for="`${componentId}-name`">Anime name:</label>
        <input class="form-control" :id="`${componentId}-name`" maxlength="128" type="text" v-model="missingAnimeData.name">
      </div>

      <div class="mb-2">
        <label class="form-label" :for="`${componentId}-link`">Link to anime:</label>
        <input class="form-control" :id="`${componentId}-link`" maxlength="200" type="url" v-model="missingAnimeData.link">
      </div>

      <div class="mb-2">
        <label class="form-label" :for="`${componentId}-description`">Extra information (optional):</label>
        <textarea class="form-control" :id="`${componentId}-description`" rows="3" v-model="missingAnimeData.description"></textarea>
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
import Ajax, { Response } from "@/util/ajax";
import NotificationService from "@/util/notification-service";

@Options({
  props: {
    missingAnimeData: Object,
    isSurveyPreseason: Boolean,
  },
  components: {
    Modal,
  },
  methods: {
    async sendMissingAnimeData(): Promise<boolean> {
      try {
        const result = await Ajax.post('api/nonexistentsomething/', this.missingAnimeData);
        if (Response.isErrorData(result.data)) {
          NotificationService.pushMsgList(result.getGlobalErrors(), 'danger');
          // TODO: Handle validation errors
          return false;
        }
      } catch {
        return false;
      }

      this.missingAnimeData.name = '';
      this.missingAnimeData.link = '';
      this.missingAnimeData.description = '';
      return true;
    },
  }
})
export default class SurveyFormMissingAnimeModal extends Vue {
  private static globalId = 0;
  componentId = `missing-anime-modal-${SurveyFormMissingAnimeModal.globalId++}`;
}
</script>