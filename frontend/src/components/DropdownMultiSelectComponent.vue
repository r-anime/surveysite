<template>
  <div class="dropdown">
    <button class="btn dropdown-toggle" :class="buttonClass" type="button" :id="dropdownId" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
      <slot></slot>
    </button>
    <ul class="dropdown-menu" :aria-labelledby="dropdownId">
      <li class="px-2" v-for="item in items" :key="item.id">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" :id="'item'+item.id" :value="item.id" v-model="selectedItemIds">
          <label class="form-check-label" :for="'item'+item.id">
            {{ item.name }}
          </label>
        </div>
      </li>
      <li><hr class="dropdown-divider"></li>
      <li class="px-2">
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="itemAll" v-model="selectAll">
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
import { computed } from "vue";

const props = withDefaults(defineProps<{
  items: SelectorItem[];
  modelValue: number[];
  buttonClass?: string;
}>(), {
  buttonClass: 'btn-primary',
});

const emit = defineEmits<{
  (e: 'update:modelValue', newSelectedItemIds: number[]): void;
}>();


const dropdownId = IdGenerator.generateUniqueId('dropdownMultiSelect');


const selectedItemIds = computed<number[]>({
  get() {
    return props.modelValue;
  },
  set(value) {
    onSelectionChanged(value);
  },
});
const selectAll = computed<boolean>({
  get() {
    return props.items.length === props.modelValue.length;
  },
  set(value) {
    onSelectionChanged(value ? props.items.map(item => item.id) : []);
  },
});


function onSelectionChanged(newSelectedItemIds: number[]): void {
  emit('update:modelValue', newSelectedItemIds);
}
</script>
