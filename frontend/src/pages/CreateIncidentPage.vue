<template>
  <q-page class="q-pa-lg">
    <div class="row items-center q-mb-lg">
      <q-btn flat icon="arrow_back" to="/incidents" dense class="q-mr-sm" />
      <div class="text-h5 text-weight-bold">Create Incident</div>
    </div>

    <div class="row justify-center">
      <div class="col-xs-12 col-md-8 col-lg-6">
        <q-card flat bordered>
          <q-card-section class="q-pa-xl">
            <q-form @submit="handleSubmit" class="q-gutter-md">
              <!-- Title -->
              <q-input
                v-model="form.title"
                label="Title *"
                outlined
                :rules="[val => !!val || 'Title is required', val => val.length >= 3 || 'Min 3 characters']"
                hint="Brief, descriptive title for the incident"
              />

              <!-- Description -->
              <q-input
                v-model="form.description"
                label="Description"
                outlined
                type="textarea"
                autogrow
                hint="Detailed description of the incident"
              />

              <!-- Priority -->
              <q-select
                v-model="form.priority"
                :options="priorityOptions"
                label="Priority *"
                outlined
                emit-value
                map-options
                :rules="[val => !!val || 'Priority is required']"
              >
                <template #option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section avatar>
                      <q-icon :name="priorityIcon(scope.opt.value)" :color="priorityColor(scope.opt.value)" />
                    </q-item-section>
                    <q-item-section>{{ scope.opt.label }}</q-item-section>
                  </q-item>
                </template>
              </q-select>

              <!-- Assign To -->
              <q-select
                v-model="form.assigned_to"
                :options="userOptions"
                label="Assign To (optional)"
                outlined
                emit-value
                map-options
                clearable
                :loading="usersStore.loading"
              />

              <!-- Error message -->
              <div v-if="errorMsg" class="text-negative text-caption">
                {{ errorMsg }}
              </div>

              <!-- Actions -->
              <div class="row q-gutter-sm justify-end q-mt-md">
                <q-btn
                  flat
                  label="Cancel"
                  to="/incidents"
                  no-caps
                />
                <q-btn
                  type="submit"
                  label="Create Incident"
                  color="primary"
                  unelevated
                  no-caps
                  :loading="store.loading"
                />
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useIncidentStore } from 'src/stores/incidents'
import { useUsersStore } from 'src/stores/users'

const router = useRouter()
const $q = useQuasar()
const store = useIncidentStore()
const usersStore = useUsersStore()

const errorMsg = ref('')

const form = reactive({
  title: '',
  description: '',
  priority: 'medium',
  assigned_to: null,
})

const priorityOptions = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Critical', value: 'critical' },
]

const userOptions = computed(() =>
  usersStore.users.map(u => ({ label: `${u.name} (${u.role})`, value: u.id }))
)

const priorityIcon = (p) => ({ low: 'arrow_downward', medium: 'remove', high: 'arrow_upward', critical: 'priority_high' }[p] || 'remove')
const priorityColor = (p) => ({ low: 'positive', medium: 'warning', high: 'orange', critical: 'negative' }[p] || 'grey')

async function handleSubmit() {
  errorMsg.value = ''
  const payload = {
    title: form.title.trim(),
    description: form.description.trim() || undefined,
    priority: form.priority,
    assigned_to: form.assigned_to || undefined,
  }

  const result = await store.createIncident(payload)
  if (result.success) {
    $q.notify({ type: 'positive', message: 'Incident created successfully' })
    router.push(`/incidents/${result.incident.id}`)
  } else {
    errorMsg.value = result.error || 'Failed to create incident'
  }
}

onMounted(() => {
  // Load users for assignment dropdown
  usersStore.fetchUsers({ per_page: 100 })
})
</script>
