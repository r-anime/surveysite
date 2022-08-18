<template>
  <div class="dropdown">
    <button :class="['btn', 'dropdown-toggle', buttonClass]" type="button" :id="dropdownId" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
      <slot></slot>
    </button>
    <ul class="dropdown-menu" :aria-labelledby="dropdownId">
      <li class="px-2" v-for="item in items" :key="item.id">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" :id="'item'+item.id" :value="item.id" v-model="scuffed.selectedItemIds">
          <label class="form-check-label" :for="'item'+item.id">
            {{ item.name }}
          </label>
        </div>
      </li>
      <li><hr class="dropdown-divider"></li>
      <li class="px-2">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="itemAll" v-model="scuffed.selectAll">
          <label class="form-check-label" for="itemAll">
            Select all
          </label>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { SelectorItem } from "@/util/data";
import IdGenerator from "@/util/id-generator";

const {
  items,
  modelValue,
  buttonClass = 'btn-primary',
} = defineProps<{
  items: SelectorItem[];
  modelValue: number[];
  buttonClass?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', newSelectedItemIds: number[]): void;
}>();


const dropdownId = IdGenerator.generateUniqueId('dropdownMultiSelect');

const scuffed = {
  get selectedItemIds(): number[] { return modelValue; },
  set selectedItemIds(value: number[]) { onSelectionChanged(value); },

  get selectAll(): boolean { return items.length === modelValue.length; },
  set selectAll(value: boolean) { onSelectionChanged(value ? items.map(item => item.id) : []); },
};

function onSelectionChanged(newSelectedItemIds: number[]): void {
  emit('update:modelValue', newSelectedItemIds);
}
</script>
