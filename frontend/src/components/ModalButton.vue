<template>
  <button :class="'btn btn-'+variant" data-bs-toggle="modal" :data-bs-target="'#'+id">
    <slot></slot>
  </button>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    id: String,
    variant: String,
  }
})
export default class ModalButton extends Vue {
  id!: string;
  variant!: string;
}
</script>
