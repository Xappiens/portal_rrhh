<template>
  <div class="flex h-screen w-screen justify-center bg-gray-100">
    <div class="mt-32 w-full px-4">
      <div class="mx-auto h-10 flex items-center justify-center">
        <span class="text-2xl font-bold text-blue-600">Portal RRHH</span>
      </div>
      <div class="mt-6 flex items-center justify-center space-x-1.5">
        <span class="text-3xl font-semibold text-gray-900">Iniciar Sesión</span>
      </div>
      <div class="mx-auto mt-6 w-full px-4 sm:w-96">
        <form
          method="POST"
          action="/api/method/login"
          @submit.prevent="submit"
        >
          <div>
            <Input
              variant="outline"
              size="md"
              :type="
                (email || '').toLowerCase() === 'administrator'
                  ? 'text'
                  : 'email'
              "
              label="Email"
              v-model="email"
              placeholder="usuario@empresa.com"
              :disabled="session.login.loading"
            />
          </div>
          <div class="mt-4">
            <Input
              variant="outline"
              size="md"
              label="Contraseña"
              v-model="password"
              placeholder="••••••"
              :disabled="session.login.loading"
              type="password"
            />
          </div>
          <ErrorMessage class="mt-2" :message="session.login.error" />
          <Button
            variant="solid"
            class="mt-6 w-full"
            :loading="session.login.loading"
          >
            Iniciar Sesión
          </Button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { sessionStore } from '@/stores/session'
import { ref } from 'vue'

const session = sessionStore()
let email = ref('')
let password = ref('')

function submit() {
  session.login.submit({
    usr: email.value,
    pwd: password.value,
  })
}
</script>
