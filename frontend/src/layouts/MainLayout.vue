<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Top Navbar -->
    <q-header elevated class="bg-grey-10 text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="toggleDrawer" />
        <q-toolbar-title class="text-weight-bold">
          <q-icon name="security" class="q-mr-sm" />
          IncidentHub
        </q-toolbar-title>
        <q-space />
        <q-chip
          :color="roleColor"
          text-color="white"
          :label="authStore.user?.role?.toUpperCase()"
          class="q-mr-md"
          dense
        />
        <q-btn-dropdown flat round dense :label="authStore.user?.name" icon="person">
          <q-list>
            <q-item clickable v-close-popup @click="logout">
              <q-item-section avatar>
                <q-icon name="logout" />
              </q-item-section>
              <q-item-section>Logout</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <!-- Sidebar -->
    <q-drawer v-model="drawer" show-if-above :width="240" :breakpoint="700" bordered>
      <q-scroll-area class="fit">
        <!-- Logo area -->
        <div class="q-pa-md bg-grey-10 text-white text-center">
          <div class="text-h6 text-weight-bold">IncidentHub</div>
          <div class="text-caption text-grey-4">{{ authStore.user?.email }}</div>
        </div>

        <q-list padding>
          <q-item
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            clickable
            exact
            active-class="bg-blue-1 text-primary text-weight-bold"
            class="rounded-borders q-my-xs"
          >
            <q-item-section avatar>
              <q-icon :name="link.icon" />
            </q-item-section>
            <q-item-section>{{ link.label }}</q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <!-- Main content -->
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const drawer = ref(false)

function toggleDrawer() {
  drawer.value = !drawer.value
}

const roleColor = computed(() => {
  const colors = { admin: 'negative', manager: 'warning', user: 'positive' }
  return colors[authStore.user?.role] || 'grey'
})

const navLinks = computed(() => {
  const links = [
    { to: '/dashboard', icon: 'dashboard', label: 'Dashboard' },
    { to: '/incidents', icon: 'report_problem', label: 'Incidents' },
  ]
  if (['admin', 'manager'].includes(authStore.user?.role)) {
    links.push({ to: '/incidents/create', icon: 'add_circle', label: 'New Incident' })
  }
  if (authStore.user?.role === 'admin') {
    links.push({ to: '/users', icon: 'group', label: 'Users' })
  }
  return links
})

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>
