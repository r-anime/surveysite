<template>
  <button :class="`btn btn-${modalButtonVariant} ${modalButtonClass}`" data-bs-toggle="modal" :data-bs-target="`#${modalId}`">
    {{ modalButtonText }}
  </button>

  <teleport to="#modals">
    <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="`${modalId}Label`" aria-hidden="true">
      <div class="modal-dialog modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" :id="`${modalId}Label`">{{ modalTitle }}</h5>
            <button class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            <slot></slot>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>


            <button v-if="acceptButtonCallback"
                    type="button"
                    class="btn btn-primary"
                    @click="acceptButtonCallbackWrapper">
              {{ acceptButtonText }}
            </button>

            <a v-else-if="acceptButtonUrl"
               :href="acceptButtonUrl"
               class="btn btn-primary">
              {{ acceptButtonText }}
            </a>

            <form v-else-if="acceptButtonPost" method="POST" :action="acceptButtonPost">
              <input type="hidden" name="csrfmiddlewaretoken" :value="getCsrfToken()">
              <button type="submit" class="btn btn-primary">{{ acceptButtonText }}</button>
            </form>

            <router-link v-else-if="acceptButtonRoute"
                         :to="acceptButtonRoute"
                         class="btn btn-primary">
              {{ acceptButtonText }}
            </router-link>

            <button v-else
                    type="button"
                    class="btn btn-primary"
                    data-bs-dismiss="modal">
              {{ acceptButtonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { Modal as BootstrapModal } from 'bootstrap';
import Cookie from 'js-cookie';
import type { RouteLocation } from 'vue-router';
import IdGenerator from '@/util/id-generator';

const {
  modalTitle,
  modalButtonClass = '',
  modalButtonVariant = 'primary',
  modalButtonText,

  acceptButtonUrl,
  acceptButtonPost,
  acceptButtonRoute,
  acceptButtonCallback,

  acceptButtonText = 'Ok',
} = defineProps<{
  modalTitle?: string;
  modalButtonClass?: string;
  modalButtonVariant?: string;
  modalButtonText?: string;
  
  acceptButtonUrl?: string;
  acceptButtonPost?: string; // Identical to acceptButtonUrl, but performs a POST instead of a GET request,
  acceptButtonRoute?: RouteLocation;
  acceptButtonCallback?: () => boolean | Promise<boolean>; // Should be a function that returns a success boolean, upon which the modal gets hidden

  acceptButtonText?: string;
}>();

const modalId = IdGenerator.generateUniqueId('modal');

function getCsrfToken(): string | undefined {
  return Cookie.get('csrftoken');
}

async function acceptButtonCallbackWrapper(): Promise<void> {
  if (acceptButtonCallback && await acceptButtonCallback()) {
    BootstrapModal.getInstance(`#${modalId}`)?.hide();
  }
}
</script>
