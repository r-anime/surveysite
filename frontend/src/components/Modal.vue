<template>
  <button :class="`btn btn-${modalButtonVariant} ${modalButtonClass}`" data-bs-toggle="modal" :data-bs-target="`#${modalId}`">
    {{ modalButtonText }}
  </button>

  <teleport to="#modals">
    <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="`${modalId}Label`" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" :id="`${modalId}Label`">{{ modalTitle }}</h5>
            <button class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
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

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import { Modal as BootstrapModal } from 'bootstrap';

@Options({
  props: {
    modalTitle: String,

    modalButtonClass: {
      type: String,
      default: '',
    },
    modalButtonVariant: {
      type: String,
      default: 'primary',
    },
    modalButtonText: String,

    acceptButtonUrl: {
      type: String,
      default: null,
    },
    acceptButtonRoute: {
      type: Object,
      default: null,
    },
    acceptButtonCallback: {
      type: Function, // Should be a function that returns a Promise<boolean>
      default: null,
    },
    acceptButtonText: {
      type: String,
      default: 'Ok',
    },
  },
  methods: {
    async acceptButtonCallbackWrapper() {
      if (this.acceptButtonCallback && await this.acceptButtonCallback()) {
        BootstrapModal.getInstance(`#${this.modalId}`)?.hide();
      }
    }
  }
})
export default class Modal extends Vue {
  private static componentId = 0;
  modalId = `modal${Modal.componentId++}`;
}
</script>
