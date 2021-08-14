<template>
  <div class="modal fade" :id="id" tabindex="-1" :aria-labelledby="id+'Label'" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" :id="id+'Label'">{{ title }}</h5>
          <button class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <slot></slot>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <a :href="acceptButtonUrl" class="btn btn-primary">{{ acceptButtonText }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    id: String,
    title: String,
    acceptButtonUrl: String,
    acceptButtonText: String,
  }
})
export default class Modal extends Vue {
  id!: string;
  title!: string;
  acceptButtonUrl!: string;
  acceptButtonText!: string;
}
</script>
