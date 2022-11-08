<template>
  <teleport to="#modals">
    <template v-for="modalData in modalDataArray" :key="modalData.modalId">
      <component :is="modalData.component"
                 :modalId="modalData.modalId"
                 :data="modalData.initData.data"
                 @onModalHide="modalData.initData.emits?.onModalHide"
                 @onModalHidden="modalData.initData.emits?.onModalHidden"
                 @onModalSuccess="modalData.initData.emits?.onModalSuccess">
      </component>
    </template>
  </teleport>
</template>

<script setup lang="ts">
import IdGenerator from '@/util/id-generator';
import { ModalService, type ModalInitViewModel } from '@/util/modal-service';
import { nextTick, shallowRef, type Component } from 'vue';

// shallowRef instead of ref since otherwise it deep-tracks component
// shallowRef only tracks reassignments
const modalDataArray = shallowRef<{
  component: Component;
  initData: ModalInitViewModel;
  modalId: string;
}[]>([]);

ModalService.subscribe(addModal);


function addModal(component: Component, initData: ModalInitViewModel) {
  const modalId = IdGenerator.generateUniqueId('modal');
  const onModalHiddenOrg = initData.emits?.onModalHidden; // Necessary because it gets overwritten, we need the original

  const onModalHiddenWrapper = () => {
    if (onModalHiddenOrg) {
      onModalHiddenOrg();
    }

    // nextTick, just to be sure (?)
    nextTick(() => {
      modalDataArray.value = modalDataArray.value.filter(i => i.modalId !== modalId);
    });
  };
  if (!initData.emits) {
    initData.emits = {};
  }
  initData.emits.onModalHidden = onModalHiddenWrapper;

  modalDataArray.value = modalDataArray.value.concat({
    component,
    initData,
    modalId,
  });
}
</script>
