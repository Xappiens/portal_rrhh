<template>
  <DesktopLayout>
    <router-view />
  </DesktopLayout>
</template>

<script>
import DesktopLayout from '@/components/Layouts/DesktopLayout.vue'

export default {
  name: 'Home',
  components: {
    DesktopLayout
  }
};
</script>
