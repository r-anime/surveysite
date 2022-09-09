<template>
  <ModalTemplate :modalId="modalId"
                 modalHeaderText="Log In"
                 @onHeaderCloseClick="hideModal()">

    <template #body>
      To fill in surveys, you must be logged in with a Reddit account.
    </template>

    <template #footer>
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>

      <form v-if="userData" method="POST" :action="userData.authenticationUrl">
        <input type="hidden" name="csrfmiddlewaretoken" :value="getCsrfToken()">
        <button type="submit" class="btn btn-primary">Log in via Reddit</button>
      </form>
    </template>

  </ModalTemplate>
</template>

<script setup lang="ts">
import Cookie from 'js-cookie';
import { ref } from 'vue';
import UserService from '@/util/user-service';
import type { AnonymousUserData } from '@/util/data';
import ModalTemplate from '@/components/ModalTemplate.vue';
import { useModal } from '@/composables/modal';
import { useRoute } from 'vue-router';

const props = defineProps<{
  modalId: string;
  data: unknown;
}>();

const emit = defineEmits<{
  (e: 'onModalHide'): void;
  (e: 'onModalHidden'): void;
  (e: 'onModalSuccess'): void;
}>();

const { hideModal } = useModal(props.modalId, emit);
const route = useRoute();
const userData = ref<AnonymousUserData | null>(null);


UserService.getUserData().then(ud => {
  if (ud?.authenticated) {
    hideModal();
  } else {
    userData.value = ud;
    Cookie.set('loginredirecturl', route.fullPath, {
      expires: 1, // number is # days
      sameSite: 'lax',
    });
  }
});

function getCsrfToken(): string | undefined {
  return Cookie.get('csrftoken');
}
</script>
