<template>
  <teleport to="#modals">
    <template v-for="(modalData, modalIdx) in modalDataArray" :key="modalIdx">
      <component :is="modalData.component" @onModalHide="modalData.onModalHide"></component>
    </template>
  </teleport>
</template>

<script setup lang="ts">
import { ModalService } from '@/util/modal-service';
import type { Component } from 'vue';

const modalDataArray: { component: Component, onModalHide: () => void }[] = [];

ModalService.subscribe(addModal);


function addModal(component: Component, onModalHide: () => void) {
  modalDataArray.push({ component, onModalHide });
}
</script>
