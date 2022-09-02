<template>
  <teleport to="#modals">
    <template v-for="(modalData, modalIdx) in modalDataArray" :key="modalIdx">
      <component :is="modalData.component"
                 :data="modalData.initData.data"
                 @onModalHide="modalData.initData.emits?.onModalHide"
                 @onModalHidden="modalData.initData.emits?.onModalHidden"
                 @onModalSuccess="modalData.initData.emits?.onModalSuccess">
      </component>
    </template>
  </teleport>
</template>

<script setup lang="ts">
import { ModalService, type ModalInitData } from '@/util/modal-service';
import { shallowRef, type Component } from 'vue';

// shallowRef instead of ref since otherwise it deep-tracks component
const modalDataArray = shallowRef<{ component: Component, initData: ModalInitData }[]>([]);

ModalService.subscribe(addModal);


function addModal(component: Component, initData: ModalInitData) {
  // Must be a reassignment, as shallowRef only tracks those
  modalDataArray.value = modalDataArray.value.concat({ component, initData });
}
</script>
