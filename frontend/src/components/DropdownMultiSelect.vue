<template>
  <div class="dropdown">
    <button :class="['btn', 'dropdown-toggle', buttonClass]" type="button" :id="dropdownId" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
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

  selectedItemIds: number[] = [];

  set selectAll(value: boolean) {
    this.selectedItemIds = value ? this.items.map(item => item.id) : [];
  }
  get selectAll(): boolean {
    return this.items.length === this.selectedItemIds.length;
  }

  dropdownId?: string;
  private static componentId = 0;

  created(): void {
    this.dropdownId = `modal${DropdownMultiSelect.componentId++}`;

    const def = this.defaultSelectedItemIds;
    if (typeof def === 'boolean') {
      this.selectedItemIds = def ? this.items.map(item => item.id) : [];
    } else {
      Object.assign(this.selectedItemIds, this.defaultSelectedItemIds);
    }

    this.$watch(() => this.selectedItemIds, (newSelectedItemIds: number[]) => {
      this.$emit('selectionChanged', newSelectedItemIds);
    }, { deep: true });
  }
}
</script>
