<template>
  <q-page class="q-pa-lg">
    <div class="row items-center q-mb-lg">
      <div class="text-h5 text-weight-bold">Incidents</div>
      <q-space />
      <q-btn
        v-if="authStore.canManageIncidents"
        to="/incidents/create"
        label="New Incident"
        icon="add"
        color="primary"
        unelevated
        no-caps
      />
    </div>

    <!-- Filters -->
    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-sm">
          <q-input
            v-model="filters.search"
            placeholder="Search incidents..."
            outlined
            dense
            class="col-xs-12 col-sm-4"
            clearable
            @update:model-value="onFilterChange"
          >
            <template #prepend><q-icon name="search" /></template>
          </q-input>
          <q-select
            v-model="filters.status"
            :options="statusOptions"
            label="Status"
            outlined
            dense
            clearable
            class="col-xs-6 col-sm-2"
            emit-value
            map-options
            @update:model-value="onFilterChange"
          />
          <q-select
            v-model="filters.priority"
            :options="priorityOptions"
            label="Priority"
            outlined
            dense
            clearable
            class="col-xs-6 col-sm-2"
            emit-value
            map-options
            @update:model-value="onFilterChange"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Loading -->
    <div v-if="store.loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="40px" />
    </div>

    <!-- Empty state -->
    <div v-else-if="!store.incidents.length" class="text-center q-pa-xl">
      <q-icon name="inbox" size="64px" color="grey-4" />
      <div class="text-h6 text-grey-5 q-mt-md">No incidents found</div>
      <div class="text-caption text-grey-4">Try adjusting your filters</div>
    </div>

    <!-- Table -->
    <q-card v-else flat bordered>
      <q-table
        :rows="store.incidents"
        :columns="columns"
        row-key="id"
        flat
        :rows-per-page-options="[]"
        hide-bottom
      >
        <template #body-cell-title="props">
          <q-td :props="props">
            <router-link :to="`/incidents/${props.row.id}`" class="text-primary text-weight-medium">
              {{ props.row.title }}
            </router-link>
          </q-td>
        </template>
        <template #body-cell-status="props">
          <q-td :props="props">
            <StatusChip :status="props.row.status" />
          </q-td>
        </template>
        <template #body-cell-priority="props">
          <q-td :props="props">
            <PriorityBadge :priority="props.row.priority" />
          </q-td>
        </template>
        <template #body-cell-created_at="props">
          <q-td :props="props">{{ formatDate(props.row.created_at) }}</q-td>
        </template>
      </q-table>
    </q-card>

    <!-- Pagination -->
    <div v-if="store.pagination?.pages > 1" class="row justify-center q-mt-md">
      <q-pagination
        v-model="currentPage"
        :max="store.pagination.pages"
        boundary-links
        @update:model-value="loadIncidents"
      />
    </div>
  </q-page>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useIncidentStore } from 'src/stores/incidents'
import { useAuthStore } from 'src/stores/auth'
import StatusChip from 'src/components/StatusChip.vue'
import PriorityBadge from 'src/components/PriorityBadge.vue'

const store = useIncidentStore()
const authStore = useAuthStore()
const currentPage = ref(1)

const filters = reactive({ search: '', status: null, priority: null })

const columns = [
  { name: 'id', label: '#', field: 'id', align: 'left', sortable: true, style: 'width: 60px' },
  { name: 'title', label: 'Title', field: 'title', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'priority', label: 'Priority', field: 'priority', align: 'left' },
  { name: 'assignee_name', label: 'Assigned To', field: 'assignee_name', align: 'left' },
  { name: 'creator_name', label: 'Created By', field: 'creator_name', align: 'left' },
  { name: 'created_at', label: 'Created', field: 'created_at', align: 'left' },
]

const statusOptions = [
  { label: 'Open', value: 'open' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Resolved', value: 'resolved' },
  { label: 'Closed', value: 'closed' },
]
const priorityOptions = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Critical', value: 'critical' },
]

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'

function onFilterChange() {
  currentPage.value = 1
  loadIncidents()
}

function loadIncidents() {
  const params = { page: currentPage.value, per_page: 20 }
  if (filters.search) params.search = filters.search
  if (filters.status) params.status = filters.status
  if (filters.priority) params.priority = filters.priority
  store.fetchIncidents(params)
}

onMounted(loadIncidents)
</script>
