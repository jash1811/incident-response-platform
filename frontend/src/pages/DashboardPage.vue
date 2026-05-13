<template>
  <q-page class="q-pa-lg">
    <div class="text-h5 text-weight-bold q-mb-lg">Dashboard</div>

    <!-- Stats cards -->
    <div class="row q-gutter-md q-mb-lg">
      <div v-for="stat in statCards" :key="stat.label" class="col-xs-12 col-sm-6 col-md-2">
        <q-card flat bordered class="stat-card text-center q-pa-md">
          <q-icon :name="stat.icon" :color="stat.color" size="36px" />
          <div class="text-h4 text-weight-bold q-mt-sm" :class="`text-${stat.color}`">
            {{ statsData[stat.key] ?? '—' }}
          </div>
          <div class="text-caption text-grey-6">{{ stat.label }}</div>
        </q-card>
      </div>
    </div>

    <!-- Priority breakdown + Recent incidents -->
    <div class="row q-gutter-md">
      <div class="col-xs-12 col-md-4">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 text-weight-bold">Priority Breakdown</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <div v-if="loading" class="text-center"><q-spinner color="primary" /></div>
            <div v-else>
              <div
                v-for="(count, priority) in statsData.priority_breakdown"
                :key="priority"
                class="row items-center q-mb-sm"
              >
                <PriorityBadge :priority="priority" class="q-mr-sm" />
                <q-linear-progress
                  :value="count / (statsData.total_incidents || 1)"
                  :color="priorityColor(priority)"
                  class="col q-mx-sm"
                  rounded
                  size="8px"
                />
                <span class="text-caption text-grey-7">{{ count }}</span>
              </div>
              <div v-if="!Object.keys(statsData.priority_breakdown || {}).length" class="text-grey-5 text-caption">
                No data yet
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-xs-12 col-md-7">
        <q-card flat bordered>
          <q-card-section class="row items-center">
            <div class="text-subtitle1 text-weight-bold">Recent Incidents</div>
            <q-space />
            <q-btn flat dense label="View All" to="/incidents" color="primary" no-caps />
          </q-card-section>
          <q-separator />
          <q-card-section class="q-pa-none">
            <div v-if="loading" class="text-center q-pa-md"><q-spinner color="primary" /></div>
            <q-list v-else separator>
              <q-item
                v-for="incident in recentIncidents"
                :key="incident.id"
                :to="`/incidents/${incident.id}`"
                clickable
              >
                <q-item-section>
                  <q-item-label class="text-weight-medium">{{ incident.title }}</q-item-label>
                  <q-item-label caption>
                    <StatusChip :status="incident.status" dense />
                    <PriorityBadge :priority="incident.priority" class="q-ml-sm" />
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label caption>{{ formatDate(incident.created_at) }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-item v-if="!recentIncidents.length">
                <q-item-section class="text-grey-5 text-center q-pa-md">No incidents yet</q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'src/boot/axios'
import StatusChip from 'src/components/StatusChip.vue'
import PriorityBadge from 'src/components/PriorityBadge.vue'

const loading = ref(false)
const statsData = ref({
  total_incidents: 0, open: 0, in_progress: 0, resolved: 0, closed: 0,
  total_users: 0, priority_breakdown: {},
})
const recentIncidents = ref([])

const statCards = [
  { key: 'total_incidents', label: 'Total', icon: 'inventory_2', color: 'grey-8' },
  { key: 'open', label: 'Open', icon: 'radio_button_unchecked', color: 'negative' },
  { key: 'in_progress', label: 'In Progress', icon: 'pending', color: 'warning' },
  { key: 'resolved', label: 'Resolved', icon: 'check_circle', color: 'positive' },
  { key: 'closed', label: 'Closed', icon: 'lock', color: 'grey-6' },
  { key: 'total_users', label: 'Users', icon: 'group', color: 'primary' },
]

const priorityColor = (p) => ({ low: 'positive', medium: 'warning', high: 'orange', critical: 'negative' }[p] || 'grey')

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/api/dashboard/stats')
    statsData.value = res.data.stats
    recentIncidents.value = res.data.recent_incidents || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-card { border-radius: 12px; }
</style>
