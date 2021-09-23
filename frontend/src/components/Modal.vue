<template>
  <button :class="`btn btn-${modalButtonVariant}`" data-bs-toggle="modal" :data-bs-target="`#${modalId}`">
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
                  data-bs-dismiss="modal"
                  @click="acceptButtonCallback">
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

@Options({
  props: {
    modalId: String,
    modalTitle: String,

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
      type: Function,
      default: null,
    },
    acceptButtonText: {
      type: String,
      default: 'Ok',
    },
  },
})
export default class Modal extends Vue {}
</script>
