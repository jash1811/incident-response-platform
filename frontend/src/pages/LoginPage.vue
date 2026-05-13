<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card class="login-card shadow-10" bordered>
      <q-card-section class="bg-grey-10 text-white text-center q-py-lg">
        <q-icon name="security" size="48px" class="q-mb-sm" />
        <div class="text-h5 text-weight-bold">IncidentHub</div>
        <div class="text-caption text-grey-4">Multi-tenant Incident Response Platform</div>
      </q-card-section>

      <q-card-section class="q-pa-xl">
        <!-- Tab switcher -->
        <q-tabs v-model="tab" dense class="q-mb-lg" active-color="primary" indicator-color="primary">
          <q-tab name="login" label="Login" />
          <q-tab name="register" label="Register" />
        </q-tabs>

        <!-- Login form -->
        <q-tab-panels v-model="tab" animated>
          <q-tab-panel name="login" class="q-pa-none">
            <q-form @submit="handleLogin" class="q-gutter-md">
              <q-input
                v-model="loginForm.email"
                label="Email"
                type="email"
                outlined
                :rules="[val => !!val || 'Email is required']"
              >
                <template #prepend><q-icon name="email" /></template>
              </q-input>
              <q-input
                v-model="loginForm.password"
                label="Password"
                :type="showPass ? 'text' : 'password'"
                outlined
                :rules="[val => !!val || 'Password is required']"
              >
                <template #prepend><q-icon name="lock" /></template>
                <template #append>
                  <q-icon
                    :name="showPass ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPass = !showPass"
                  />
                </template>
              </q-input>
              <div v-if="authStore.error" class="text-negative text-caption">
                {{ authStore.error }}
              </div>
              <q-btn
                type="submit"
                label="Login"
                color="primary"
                unelevated
                class="full-width"
                :loading="authStore.loading"
              />
            </q-form>
          </q-tab-panel>

          <!-- Register form -->
          <q-tab-panel name="register" class="q-pa-none">
            <q-form @submit="handleRegister" class="q-gutter-md">
              <q-input
                v-model="registerForm.tenant_name"
                label="Organization Name"
                outlined
                :rules="[val => !!val || 'Organization name is required']"
              >
                <template #prepend><q-icon name="business" /></template>
              </q-input>
              <q-input
                v-model="registerForm.name"
                label="Full Name"
                outlined
                :rules="[val => !!val || 'Name is required']"
              >
                <template #prepend><q-icon name="person" /></template>
              </q-input>
              <q-input
                v-model="registerForm.email"
                label="Email"
                type="email"
                outlined
                :rules="[val => !!val || 'Email is required']"
              >
                <template #prepend><q-icon name="email" /></template>
              </q-input>
              <q-input
                v-model="registerForm.password"
                label="Password"
                :type="showPass ? 'text' : 'password'"
                outlined
                :rules="[val => val?.length >= 6 || 'Min 6 characters']"
              >
                <template #prepend><q-icon name="lock" /></template>
                <template #append>
                  <q-icon
                    :name="showPass ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPass = !showPass"
                  />
                </template>
              </q-input>
              <div v-if="authStore.error" class="text-negative text-caption">
                {{ authStore.error }}
              </div>
              <q-btn
                type="submit"
                label="Create Organization & Account"
                color="primary"
                unelevated
                class="full-width"
                :loading="authStore.loading"
              />
            </q-form>
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const tab = ref('login')
const showPass = ref(false)

const loginForm = reactive({ email: '', password: '' })
const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  tenant_name: '',
  role: 'admin',
})

async function handleLogin() {
  const ok = await authStore.login(loginForm.email, loginForm.password)
  if (ok) router.push('/dashboard')
}

async function handleRegister() {
  const ok = await authStore.register(registerForm)
  if (ok) router.push('/dashboard')
}
</script>

<style scoped>
.login-card {
  width: 100%;
  max-width: 440px;
  border-radius: 16px;
}
</style>
