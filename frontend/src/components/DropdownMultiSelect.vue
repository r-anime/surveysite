<template>
  <div class="dropdown">
    <button :class="['btn', 'dropdown-toggle', buttonClass]" type="button" :id="dropdownId" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
      <slot></slot>
    </button>
    <ul class="dropdown-menu" :aria-labelledby="dropdownId">
      <li v-for="item in items" :key="item.id" class="form-check">
        <input class="form-check-input" type="checkbox" :id="'item'+item.id" v-model="selectedItems[item.id]">
        <label class="form-check-label" :for="'item'+item.id">
          {{ item.name }}
        </label>
      </li>
    </ul>
  </div>
</template>
<script lang="ts">
import { SelectorItem } from "@/util/data";
import { Options, Vue } from "vue-class-component";

@Options({
  props: {
    items: {
      type: Array,
      required: true,
    },
    defaultSelectedItemIds: {
      type: [Array, Boolean],
      default: false,
    },
    buttonClass: {
      type: String,
      default: 'btn-primary',
    },
  },
  emits: ['selectionChanged'],
})
export default class DropdownMultiSelect extends Vue {
  items!: SelectorItem[];
  defaultSelectedItemIds!: number[] | boolean;

  selectedItems: Record<number, boolean> = {};

  dropdownId?: string;
  private static componentId = 0;

  created(): void {
    this.dropdownId = `modal${DropdownMultiSelect.componentId++}`;

    const def = this.defaultSelectedItemIds;
    if (typeof def === 'boolean') {
      this.items.forEach(item => this.selectedItems[item.id] = def);
    } else {
      this.items.forEach(item => this.selectedItems[item.id] = def.includes(item.id));
    }

    this.$watch(() => this.selectedItems, (newSelectedItems: Record<number, boolean>) => {
      this.$emit('selectionChanged', Object.entries(newSelectedItems).filter(item => item[1]).map(item => Number(item[0])));
    }, { deep: true });
  }
}
</script>
