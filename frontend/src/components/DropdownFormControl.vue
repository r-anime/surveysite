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
import type { SelectInputOptions } from '@/util/data';
import { computed } from 'vue';

const props = defineProps<{
  id: string;
  modelValue: T | null | undefined;
  validationErrors?: string[];
  options: SelectInputOptions<T>;
}>();

const emits = defineEmits<{
  (e: 'update:modelValue', value: T): void;
}>();

const selectedOptionId = computed<string>({
  get() {
    const selectedOption = props.options.getOptionByValueOrFirst(props.modelValue);
    return selectedOption.id;
  },
  set(optionId: string) {
    const selectedOption = props.options.getOptionByIdOrFirst(optionId);
    emits('update:modelValue', selectedOption.value);
  },
});
</script>
