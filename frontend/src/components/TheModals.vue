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
import { ModalService, type ModalInitData } from '@/util/modal-service';
import { nextTick, shallowRef, type Component } from 'vue';

// shallowRef instead of ref since otherwise it deep-tracks component
// shallowRef only tracks reassignments
const modalDataArray = shallowRef<{
  component: Component;
  initData: ModalInitData;
  modalId: string;
}[]>([]);

ModalService.subscribe(addModal);


function addModal(component: Component, initData: ModalInitData) {
  const modalId = IdGenerator.generateUniqueId('modal');

  const onModalHiddenWrapper = () => {
    if (initData.emits?.onModalHidden) {
      initData.emits?.onModalHidden();
    }

    // nextTick, just to be sure (?)
    nextTick(() => {
      modalDataArray.value = modalDataArray.value.filter(i => i.modalId !== modalId);
    });
  };
  const initDataOverwrites: ModalInitData = { emits: { onModalHidden: onModalHiddenWrapper } };

  modalDataArray.value = modalDataArray.value.concat({
    component,
    initData: Object.assign({}, initData, initDataOverwrites), // Target object empty to avoid overwriting initData
    modalId,
  });
}
</script>
