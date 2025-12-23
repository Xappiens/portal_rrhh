<template>
  <Dropdown :options="dropdownOptions">
    <template v-slot="{ open }">
      <button
        class="flex h-12 items-center rounded-md py-2 duration-300 ease-in-out"
        :class="
          isCollapsed
            ? 'w-auto px-0'
            : open
            ? 'w-52 bg-white px-2 shadow-sm'
            : 'w-52 px-2 hover:bg-gray-200'
        "
      >
        <PortalRRHHLogo />
        <div
          class="flex flex-1 flex-col text-left duration-300 ease-in-out"
          :class="
            isCollapsed
              ? 'ml-0 w-0 overflow-hidden opacity-0'
              : 'ml-2 w-auto opacity-100'
          "
        >
          <div class="text-base font-medium leading-none text-gray-900">
            Portal RRHH
          </div>
          <div class="mt-1 text-sm leading-none text-gray-700">
            {{ usersStore().getUser('sessionUser').full_name }}
          </div>
        </div>
        <div
          class="duration-300 ease-in-out"
          :class="
            isCollapsed
              ? 'ml-0 w-0 overflow-hidden opacity-0'
              : 'ml-2 w-auto opacity-100'
          "
        >
          <FeatherIcon
            name="chevron-down"
            class="size-4 text-gray-600"
            aria-hidden="true"
          />
        </div>
      </button>
    </template>
  </Dropdown>
</template>

<script setup>
import { Dropdown, FeatherIcon } from 'frappe-ui'
import { computed, ref } from 'vue'
import PortalRRHHLogo from '@/components/Icons/PortalRRHHLogo.vue'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'

const props = defineProps({
  isCollapsed: {
    type: Boolean,
    default: false,
  },
})

    const session = sessionStore()
    
    let dropdownOptions = ref([
      {
        group: 'Gestionar',
        hideLabel: true,
        items: [
          {
            icon: 'corner-up-left',
            label: 'Cambiar a Escritorio',
            handler: () => window.location.replace('/app'),
          },
          {
            icon: 'life-buoy',
            label: 'Soporte',
            handler: () => window.location.replace('/helpdesk'),
          },
        ],
      },
      {
        group: 'Cerrar Sesión',
        hideLabel: true,
        items: [
          {
            icon: 'log-out',
            label: 'Cerrar Sesión',
            handler: () => {
              session.logout.submit()
            },
          },
        ],
      },
    ])
</script>
