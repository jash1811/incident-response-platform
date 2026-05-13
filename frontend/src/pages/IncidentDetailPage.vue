<template>
  <q-page class="q-pa-lg">
    <div v-if="store.loading && !store.currentIncident" class="text-center q-pa-xl">
      <q-spinner color="primary" size="48px" />
    </div>

    <div v-else-if="!store.currentIncident" class="text-center q-pa-xl">
      <q-icon name="error_outline" size="64px" color="grey-4" />
      <div class="text-h6 text-grey-5 q-mt-md">Incident not found</div>
      <q-btn to="/incidents" label="Back to Incidents" flat color="primary" class="q-mt-md" no-caps />
    </div>

    <div v-else>
      <!-- Header -->
      <div class="row items-start q-mb-lg">
        <div>
          <q-btn flat icon="arrow_back" to="/incidents" dense class="q-mr-sm" />
          <span class="text-h6 text-weight-bold">{{ store.currentIncident.title }}</span>
          <div class="row items-center q-mt-xs q-gutter-sm">
            <StatusChip :status="store.currentIncident.status" />
            <PriorityBadge :priority="store.currentIncident.priority" />
            <span class="text-caption text-grey-6">#{{ store.currentIncident.id }}</span>
          </div>
        </div>
        <q-space />
        <!-- Actions for manager/admin -->
        <div v-if="authStore.canManageIncidents" class="row q-gutter-sm">
          <q-btn
            v-if="store.currentIncident.status !== 'resolved'"
            label="Resolve"
            icon="check_circle"
            color="positive"
            unelevated
            no-caps
            @click="resolveDialog = true"
          />
          <q-btn
            label="Assign"
            icon="person_add"
            color="primary"
            unelevated
            no-caps
            @click="assignDialog = true"
          />
          <q-btn
            label="Edit"
            icon="edit"
            color="grey-7"
            unelevated
            no-caps
            @click="editDialog = true"
          />
        </div>
      </div>

      <div class="row q-gutter-md">
        <!-- Main content -->
        <div class="col-xs-12 col-md-8">
          <!-- Description -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section>
              <div class="text-subtitle2 text-weight-bold q-mb-sm">Description</div>
              <div class="text-body2">{{ store.currentIncident.description || 'No description provided.' }}</div>
            </q-card-section>
          </q-card>

          <!-- Comments -->
          <q-card flat bordered class="q-mb-md">
            <q-card-section>
              <div class="text-subtitle2 text-weight-bold q-mb-md">
                Comments ({{ store.comments.length }})
              </div>
              <div v-if="!store.comments.length" class="text-grey-5 text-caption q-mb-md">
                No comments yet. Be the first to comment.
              </div>
              <div
                v-for="c in store.comments"
                :key="c.id"
                class="comment-item q-pa-sm q-mb-sm rounded-borders bg-grey-1"
              >
                <div class="row items-center q-mb-xs">
                  <q-avatar size="28px" color="primary" text-color="white" class="q-mr-sm">
                    {{ c.author_name?.[0]?.toUpperCase() }}
                  </q-avatar>
                  <span class="text-weight-medium text-caption">{{ c.author_name }}</span>
                  <q-space />
                  <span class="text-caption text-grey-5">{{ formatDateTime(c.created_at) }}</span>
                </div>
                <div class="text-body2 q-pl-lg">{{ c.comment }}</div>
              </div>
              <!-- Add comment -->
              <q-separator class="q-my-md" />
              <div class="row q-gutter-sm items-end">
                <q-input
                  v-model="newComment"
                  placeholder="Write a comment..."
                  outlined
                  dense
                  autogrow
                  class="col"
                />
                <q-btn
                  icon="send"
                  color="primary"
                  unelevated
                  :loading="submittingComment"
                  @click="submitComment"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Sidebar info + Activity -->
        <div class="col-xs-12 col-md-3">
          <q-card flat bordered class="q-mb-md">
            <q-card-section>
              <div class="text-subtitle2 text-weight-bold q-mb-md">Details</div>
              <detail-row label="Assigned To" :value="store.currentIncident.assignee_name || 'Unassigned'" />
              <detail-row label="Created By" :value="store.currentIncident.creator_name" />
              <detail-row label="Created" :value="formatDate(store.currentIncident.created_at)" />
              <detail-row label="Updated" :value="formatDate(store.currentIncident.updated_at)" />
              <detail-row label="Version" :value="`v${store.currentIncident.version}`" />
            </q-card-section>
          </q-card>

          <!-- Activity Timeline -->
          <q-card flat bordered>
            <q-card-section>
              <div class="text-subtitle2 text-weight-bold q-mb-md">Activity</div>
              <div v-if="!store.activity.length" class="text-grey-5 text-caption">No activity yet.</div>
              <q-timeline color="primary" dense>
                <q-timeline-entry
                  v-for="log in store.activity"
                  :key="log.id"
                  :subtitle="formatDateTime(log.created_at)"
                  :title="log.actor_name"
                >
                  <div class="text-caption">
                    <span class="text-weight-medium">{{ formatAction(log.action) }}</span>
                    <span v-if="log.old_value && log.new_value">:
                      <span class="text-strikethrough text-grey-6">{{ log.old_value }}</span>
                      → <span class="text-positive">{{ log.new_value }}</span>
                    </span>
                  </div>
                </q-timeline-entry>
              </q-timeline>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Resolve Dialog -->
    <q-dialog v-model="resolveDialog">
      <q-card style="min-width: 320px">
        <q-card-section>
          <div class="text-h6">Resolve Incident?</div>
          <div class="text-body2 text-grey-7">This will mark the incident as resolved.</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup no-caps />
          <q-btn color="positive" label="Resolve" unelevated no-caps @click="confirmResolve" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Assign Dialog -->
    <q-dialog v-model="assignDialog">
      <q-card style="min-width: 360px">
        <q-card-section>
          <div class="text-h6">Assign Incident</div>
        </q-card-section>
        <q-card-section>
          <q-select
            v-model="selectedAssignee"
            :options="userOptions"
            label="Select User"
            outlined
            emit-value
            map-options
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup no-caps />
          <q-btn color="primary" label="Assign" unelevated no-caps @click="confirmAssign" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Dialog -->
    <q-dialog v-model="editDialog" full-width>
      <q-card>
        <q-card-section>
          <div class="text-h6">Edit Incident</div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input v-model="editForm.title" label="Title" outlined />
          <q-input v-model="editForm.description" label="Description" outlined autogrow />
          <q-select
            v-model="editForm.status"
            :options="statusOptions"
            label="Status"
            outlined
            emit-value
            map-options
          />
          <q-select
            v-model="editForm.priority"
            :options="priorityOptions"
            label="Priority"
            outlined
            emit-value
            map-options
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup no-caps />
          <q-btn color="primary" label="Save" unelevated no-caps @click="confirmEdit" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, reactive, computed, onMounted, defineComponent, h } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { useIncidentStore } from 'src/stores/incidents'
import { useAuthStore } from 'src/stores/auth'
import { useUsersStore } from 'src/stores/users'
import StatusChip from 'src/components/StatusChip.vue'
import PriorityBadge from 'src/components/PriorityBadge.vue'

const route = useRoute()
const $q = useQuasar()
const store = useIncidentStore()
const authStore = useAuthStore()
const usersStore = useUsersStore()

// Inline detail row component
const DetailRow = defineComponent({
  props: ['label', 'value'],
  setup(props) {
    return () => h('div', { class: 'row q-mb-sm' }, [
      h('div', { class: 'text-grey-6 text-caption col-5' }, props.label),
      h('div', { class: 'text-caption text-weight-medium col' }, props.value || '—'),
    ])
  }
})

const newComment = ref('')
const submittingComment = ref(false)
const resolveDialog = ref(false)
const assignDialog = ref(false)
const editDialog = ref(false)
const selectedAssignee = ref(null)
const editForm = reactive({ title: '', description: '', status: '', priority: '' })

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

const userOptions = computed(() =>
  usersStore.users.map(u => ({ label: u.name, value: u.id }))
)

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'
const formatDateTime = (d) => d ? new Date(d).toLocaleString() : '—'
const formatAction = (a) => a?.replace(/_/g, ' ')

async function submitComment() {
  if (!newComment.value.trim()) return
  submittingComment.value = true
  const result = await store.addComment(route.params.id, newComment.value)
  if (result.success) {
    newComment.value = ''
  } else {
    $q.notify({ type: 'negative', message: result.error })
  }
  submittingComment.value = false
}

async function confirmResolve() {
  resolveDialog.value = false
  const result = await store.resolveIncident(route.params.id, store.currentIncident.version)
  if (result.success) {
    $q.notify({ type: 'positive', message: 'Incident resolved' })
    store.fetchActivity(route.params.id)
  } else {
    $q.notify({ type: 'negative', message: result.error })
  }
}

async function confirmAssign() {
  if (!selectedAssignee.value) return
  assignDialog.value = false
  const result = await store.assignIncident(route.params.id, selectedAssignee.value, store.currentIncident.version)
  if (result.success) {
    $q.notify({ type: 'positive', message: 'Incident assigned' })
    store.fetchActivity(route.params.id)
  } else {
    $q.notify({ type: 'negative', message: result.error })
  }
}

async function confirmEdit() {
  editDialog.value = false
  const payload = { ...editForm, version: store.currentIncident.version }
  const result = await store.updateIncident(route.params.id, payload)
  if (result.success) {
    $q.notify({ type: 'positive', message: 'Incident updated' })
    store.fetchActivity(route.params.id)
  } else {
    $q.notify({ type: 'negative', message: result.error })
  }
}

onMounted(async () => {
  const id = route.params.id
  await store.fetchIncident(id)
  if (store.currentIncident) {
    editForm.title = store.currentIncident.title
    editForm.description = store.currentIncident.description || ''
    editForm.status = store.currentIncident.status
    editForm.priority = store.currentIncident.priority
  }
  await Promise.all([
    store.fetchComments(id),
    store.fetchActivity(id),
    usersStore.fetchUsers({ per_page: 100 }),
  ])
})
</script>

<style scoped>
.comment-item { border-left: 3px solid #1976d2; }
</style>
