<template>
  <label :for="id" class="form-label">
    <slot></slot>
  </label>
  <select :id="id"
          class="form-select"
          :class="{'is-invalid': validationErrors?.length}"
          autocomplete="off"
          v-model="selectedOptionId">
    <option v-for="option in options"
            :key="option.id"
            :value="option.id">
      {{ option.displayName }}
    </option>
  </select>
  <FormValidationErrors :id="`${id}-invalid`"
                        :validationErrors="validationErrors"/>
</template>

<script setup lang="ts" generic="T">
import FormValidationErrors from '@/components/FormValidationErrors.vue';
import type { SelectInputOption } from '@/util/data';
import { computed } from 'vue';

const props = defineProps<{
  id: string;
  modelValue: T | null | undefined;
  validationErrors?: string[];
  options: SelectInputOption<T>[];
}>();

const emits = defineEmits<{
  (e: 'update:modelValue', value: T): void;
}>();

const selectedOptionId = computed<string>({
  get() {
    const selectedOption = props.options.find(option => option.value === props.modelValue) ?? props.options[0];
    return selectedOption.id;
  },
  set(optionId: string) {
    const selectedOption = props.options.find(option => option.id === optionId) ?? props.options[0];
    emits('update:modelValue', selectedOption.value);
  },
});
</script>
