<template>
  <div class="dropdown">
    <button :id="dropdownId"
            type="button"
            class="btn dropdown-toggle"
            :class="buttonClass"
            data-bs-toggle="dropdown"
            data-bs-auto-close="outside"
            aria-expanded="false">
      <slot></slot>
    </button>
    <ul class="dropdown-menu" :aria-labelledby="dropdownId">
      <li class="px-2"
          v-for="option in options"
          :key="option.id">
        <div class="form-check">
          <input :id="'option'+option.id"
                 type="checkbox"
                 class="form-check-input"
                 :value="option.id"
                 v-model="selectedOptionIds">
          <label class="form-check-label"
                 :for="'option'+option.id">
            {{ option.displayName }}
          </label>
        </div>
      </li>
      <li><hr class="dropdown-divider"></li>
      <li class="px-2">
        <div class="form-check">
          <input id="optionAll"
                 type="checkbox"
                 class="form-check-input"
                 v-model="selectAll">
          <label class="form-check-label"
                 for="optionAll">
            Select all
          </label>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { ResultType, SelectInputOptions } from "@/util/data";
import IdGenerator from "@/util/id-generator";
import { computed } from "vue";

const props = withDefaults(defineProps<{
  options: SelectInputOptions<ResultType>,
  modelValue: ResultType[];
  buttonClass?: string;
}>(), {
  buttonClass: 'btn-primary',
});

const emit = defineEmits<{
  (e: 'update:modelValue', newSelectedOptionIds: ResultType[]): void;
}>();


const dropdownId = IdGenerator.generateUniqueId('dropdownMultiSelect');

const originalModelValues = props.modelValue;

function isNotNil<T>(value: T | null | undefined): value is T {
  return value != null;
}

const selectedOptionIds = computed<string[]>({
  get() {
    return props.modelValue.map(value => props.options.getOptionByValue(value)?.id).filter(isNotNil);
  },
  set(ids) {
    emit('update:modelValue', ids.map(id => props.options.getOptionById(id)?.value).filter(isNotNil));
  },
});
const selectAll = computed<boolean>({
  get() {
    return props.options.length === props.modelValue.length;
  },
  set(value) {
    onSelectionChanged(value ? props.options.map(option => option.value) : originalModelValues);
  },
});


function onSelectionChanged(newSelectedOptionIds: number[]): void {
  emit('update:modelValue', newSelectedOptionIds);
}
</script>
