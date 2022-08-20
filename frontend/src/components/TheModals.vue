<template>
  <teleport to="#modals">
    <template v-for="(modalData, modalIdx) in modalDataArray" :key="modalIdx">
      <component :is="modalData.component" @onModalHide="modalData.onModalHide" :data="modalData.data"></component>
    </template>
  </teleport>
</template>

<script setup lang="ts">
import { ModalService } from '@/util/modal-service';
import { shallowRef, type Component } from 'vue';

// shallowRef instead of ref since otherwise it deep-tracks component
const modalDataArray = shallowRef<{ component: Component, onModalHide: (success: boolean) => void, data?: unknown }[]>([]);

ModalService.subscribe(addModal);


function addModal(component: Component, onModalHide: (success: boolean) => void, data?: unknown) {
  // Must be a reassignment, as shallowRef only tracks those
  modalDataArray.value = modalDataArray.value.concat({ component, onModalHide, data });
}
</script>
