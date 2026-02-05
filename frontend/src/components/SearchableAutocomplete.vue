<template>
  <Combobox v-model="selectedValue" nullable v-slot="{ open: isComboboxOpen }">
    <div class="relative w-full">
      <div class="w-full">
        <ComboboxButton
          class="flex w-full items-center justify-between rounded-md bg-gray-100 py-1 pl-3 pr-2 transition-colors hover:bg-gray-200"
          :class="{ 'rounded-b-none': isComboboxOpen }"
        >
          <span
            class="overflow-hidden text-ellipsis text-base leading-5"
            v-if="selectedValue"
          >
            {{ displayValue(selectedValue) }}
          </span>
          <span class="text-base leading-5 text-gray-500" v-else>
            {{ placeholder || 'Select...' }}
          </span>
          <FeatherIcon
            name="chevron-down"
            class="h-4 w-4 text-gray-500"
            aria-hidden="true"
          />
        </ComboboxButton>
      </div>
      <transition
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <ComboboxOptions
          class="absolute z-10 max-h-[15rem] w-full overflow-y-auto rounded-md rounded-t-none bg-white px-1.5 pb-1.5 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
          v-show="isComboboxOpen"
        >
          <div
            class="sticky top-0 mb-1.5 flex items-stretch space-x-1.5 bg-white pt-1.5"
          >
            <ComboboxInput
              class="form-input w-full placeholder-gray-500 text-sm"
              type="text"
              @change="(e) => { query = e.target.value }"
              :value="query"
              autocomplete="off"
              :placeholder="placeholder || 'Search...'"
            />
          </div>
          <div
            v-for="group in groups"
            :key="group.key"
            v-show="group.items.length > 0"
          >
            <div
              v-if="group.group && !group.hideLabel"
              class="px-2 py-1 text-xs font-semibold uppercase tracking-wider text-gray-500"
            >
              {{ group.group }}
            </div>
            <ComboboxOption
              as="template"
              v-for="option in group.items"
              :key="option.value"
              :value="option"
              v-slot="{ active, selected }"
            >
              <li
                :class="[
                  'relative cursor-default select-none rounded-md px-2.5 py-1.5 text-base',
                  { 'bg-gray-100 text-gray-900': active, 'text-gray-900': !active },
                ]"
              >
                <span class="block truncate" :class="{ 'font-medium': selected }">
                  {{ option.label }}
                </span>
              </li>
            </ComboboxOption>
          </div>
          <li
            v-if="groups.length == 0"
            class="rounded-md px-2.5 py-1.5 text-base text-gray-600"
          >
            No results found
          </li>
        </ComboboxOptions>
      </transition>
    </div>
  </Combobox>
</template>

<script>
import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
  ComboboxButton,
} from '@headlessui/vue'
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'SearchableAutocomplete',
  props: ['modelValue', 'options', 'placeholder'],
  emits: ['update:modelValue', 'update:query'],
  components: {
    FeatherIcon,
    Combobox,
    ComboboxInput,
    ComboboxOptions,
    ComboboxOption,
    ComboboxButton,
  },
  data() {
    return {
      query: '',
    }
  },
  watch: {
    query(val) {
      this.$emit('update:query', val)
    }
  },
  computed: {
    valuePropPassed() {
      return 'value' in this.$attrs
    },
    selectedValue: {
      get() {
        return this.valuePropPassed ? this.$attrs.value : this.modelValue
      },
      set(val) {
        // Do not verify match, just emit.
        // But if val is null, we clear query? Maybe.
        if (val === null) {
            // keep query?
        }
        this.$emit(this.valuePropPassed ? 'change' : 'update:modelValue', val)
      },
    },
    groups() {
      if (!this.options || this.options.length == 0) return []

      let groups = this.options[0]?.group
        ? this.options
        : [{ group: '', items: this.options }]

      return groups
        .map((group, i) => {
          return {
            key: i,
            group: group.group,
            hideLabel: group.hideLabel || false,
            items: group.items, // WE DO NOT FILTER HERE. Server does it.
          }
        })
        .filter((group) => group.items.length > 0)
    },
  },
  methods: {
    displayValue(option) {
      if (!option) return ''
      if (typeof option === 'string') {
        return option
      }
      return option?.label
    },
  },
}
</script>
