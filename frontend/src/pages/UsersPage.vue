<template>
  <q-page class="q-pa-lg">
    <div class="row items-center q-mb-lg">
      <div class="text-h5 text-weight-bold">User Management</div>
      <q-space />
      <q-btn
        label="Add User"
        icon="person_add"
        color="primary"
        unelevated
        no-caps
        @click="createDialog = true"
      />
    </div>

    <!-- Loading -->
    <div v-if="store.loading && !store.users.length" class="text-center q-pa-xl">
      <q-spinner color="primary" size="40px" />
    </div>

    <!-- Empty state -->
    <div v-else-if="!store.users.length" class="text-center q-pa-xl">
      <q-icon name="group_off" size="64px" color="grey-4" />
      <div class="text-h6 text-grey-5 q-mt-md">No users yet</div>
      <div class="text-caption text-grey-4">Add your first team member</div>
    </div>

    <!-- Users table -->
    <q-card v-else flat bordered>
      <q-table
        :rows="store.users"
        :columns="columns"
        row-key="id"
        flat
        :rows-per-page-options="[10, 20, 50]"
      >
        <template #body-cell-role="props">
          <q-td :props="props">
            <q-chip
              :color="roleColor(props.row.role)"
              text-color="white"
              :label="props.row.role.toUpperCase()"
              dense
              square
              class="text-weight-bold"
              style="font-size: 11px"
            />
          </q-td>
        </template>
        <template #body-cell-created_at="props">
          <q-td :props="props">{{ formatDate(props.row.created_at) }}</q-td>
        </template>
        <template #body-cell-actions="props">
          <q-td :props="props">
            <!-- TODO: add edit/deactivate actions in future iteration -->
            <q-btn flat round dense icon="more_vert" size="sm">
              <q-menu>
                <q-list dense>
                  <q-item clickable v-close-popup @click="viewUser(props.row)">
                    <q-item-section avatar><q-icon name="visibility" /></q-item-section>
                    <q-item-section>View</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <!-- Pagination -->
    <div v-if="store.pagination?.pages > 1" class="row justify-center q-mt-md">
      <q-pagination
        v-model="currentPage"
        :max="store.pagination.pages"
        boundary-links
        @update:model-value="loadUsers"
      />
    </div>

    <!-- Create User Dialog -->
    <q-dialog v-model="createDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="bg-grey-10 text-white">
          <div class="text-h6">Add New User</div>
        </q-card-section>

        <q-card-section class="q-pa-lg">
          <q-form @submit="handleCreateUser" class="q-gutter-md">
            <q-input
              v-model="newUser.name"
              label="Full Name *"
              outlined
              dense
              :rules="[val => !!val || 'Name is required']"
            />
            <q-input
              v-model="newUser.email"
              label="Email *"
              type="email"
              outlined
              dense
              :rules="[val => !!val || 'Email is required']"
            />
            <q-input
              v-model="newUser.password"
              label="Password *"
              :type="showPass ? 'text' : 'password'"
              outlined
              dense
              :rules="[val => val?.length >= 6 || 'Min 6 characters']"
            >
              <template #append>
                <q-icon
                  :name="showPass ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="showPass = !showPass"
                />
              </template>
            </q-input>
            <q-select
              v-model="newUser.role"
              :options="roleOptions"
              label="Role *"
              outlined
              dense
              emit-value
              map-options
            />

            <div v-if="store.error" class="text-negative text-caption">
              {{ store.error }}
            </div>

            <div class="row q-gutter-sm justify-end q-mt-sm">
              <q-btn flat label="Cancel" v-close-popup no-caps @click="resetForm" />
              <q-btn
                type="submit"
                label="Create User"
                color="primary"
                unelevated
                no-caps
                :loading="store.loading"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- View User Dialog -->
    <q-dialog v-model="viewDialog">
      <q-card style="min-width: 360px">
        <q-card-section class="bg-grey-10 text-white row items-center">
          <q-avatar color="primary" text-color="white" class="q-mr-md">
            {{ selectedUser?.name?.[0]?.toUpperCase() }}
          </q-avatar>
          <div>
            <div class="text-h6">{{ selectedUser?.name }}</div>
            <div class="text-caption text-grey-4">{{ selectedUser?.email }}</div>
          </div>
        </q-card-section>
        <q-card-section>
          <div class="row q-mb-sm">
            <div class="text-grey-6 col-4">Role</div>
            <q-chip
              :color="roleColor(selectedUser?.role)"
              text-color="white"
              :label="selectedUser?.role?.toUpperCase()"
              dense square
              style="font-size: 11px"
            />
          </div>
          <div class="row q-mb-sm">
            <div class="text-grey-6 col-4">Joined</div>
            <div>{{ formatDate(selectedUser?.created_at) }}</div>
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" v-close-popup no-caps />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useUsersStore } from 'src/stores/users'

const $q = useQuasar()
const store = useUsersStore()
const currentPage = ref(1)
const createDialog = ref(false)
const viewDialog = ref(false)
const showPass = ref(false)
const selectedUser = ref(null)

const newUser = reactive({
  name: '',
  email: '',
  password: '',
  role: 'user',
})

const columns = [
  { name: 'id', label: '#', field: 'id', align: 'left', sortable: true, style: 'width: 60px' },
  { name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'role', label: 'Role', field: 'role', align: 'left' },
  { name: 'created_at', label: 'Joined', field: 'created_at', align: 'left' },
  { name: 'actions', label: '', field: 'actions', align: 'right' },
]

const roleOptions = [
  { label: 'Admin', value: 'admin' },
  { label: 'Manager', value: 'manager' },
  { label: 'User', value: 'user' },
]

const roleColor = (r) => ({ admin: 'negative', manager: 'warning', user: 'positive' }[r] || 'grey')
const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'

function viewUser(user) {
  selectedUser.value = user
  viewDialog.value = true
}

function resetForm() {
  newUser.name = ''
  newUser.email = ''
  newUser.password = ''
  newUser.role = 'user'
  showPass.value = false
}

async function handleCreateUser() {
  const result = await store.createUser({ ...newUser })
  if (result.success) {
    $q.notify({ type: 'positive', message: `User ${result.user.name} created` })
    createDialog.value = false
    resetForm()
  }
  // error is shown inline via store.error
}

function loadUsers() {
  store.fetchUsers({ page: currentPage.value, per_page: 20 })
}

onMounted(loadUsers)
</script>
