<template>
  <ModalTemplate :modalId="modalId"
                 modalHeaderText="Your response was succesfully submitted!"
                 @onHeaderCloseClick="hideModal()">

    <template #body>
      <div class="row row-cols-1">
        <p class="col">
          To edit your response in the future, save the link below. Without this link, you will not be able to edit your response. Do not share it either, as others could then also edit your response.
        </p>
        <div class="col">
          <RouterLink :to="editRoute">
            <!-- Visibility toggle? -->
            {{ editRoute.fullPath }}
          </RouterLink>
        </div>
      </div>
    </template>

    <template #footer>
      <button type="button"
              class="btn btn-primary"
              @click="hideModal(true)">
        Continue
      </button>
    </template>
    
  </ModalTemplate>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import ModalTemplate from '@/components/ModalTemplate.vue';
import { useModal } from '@/composables/modal';

const props = defineProps<{
  data: string;
}>();

const emit = defineEmits<{
  (e: 'onModalHide'): void;
  (e: 'onModalHidden'): void;
  (e: 'onModalSuccess'): void;
}>();

const { modalId, hideModal } = useModal(emit);
const router = useRouter();
const editRoute = router.resolve({ name: 'SurveyForm', query: { responseId: props.data }});
</script>
