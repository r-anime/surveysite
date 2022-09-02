<template>
  <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="`${modalId}Label`" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">

        <div class="modal-header">
          <slot name="header">
            <h5 class="modal-title" :id="`${modalId}Label`">{{ modalHeaderText }}</h5>
            <button class="btn-close" @click="emit('onHide')" aria-label="Close"></button>
          </slot>
        </div>

        <div class="modal-body p-4">
          <slot name="body"></slot>
        </div>

        <div class="modal-footer">
          <slot name="footer">
            <button type="button" class="btn btn-secondary" @click="emit('onHide')">Cancel</button>

            <button type="button"
                    class="btn btn-primary"
                    @click="emit('onSuccess')">
              {{ modalFooterSuccessButtonText }}
            </button>
          </slot>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// This component should not have any real logic

defineProps<{
  modalId: string;
  modalHeaderText?: string;
  modalFooterSuccessButtonText?: string;
}>();

const emit = defineEmits<{
  (e: 'onHide'): void;
  (e: 'onSuccess'): void;
}>();
</script>
