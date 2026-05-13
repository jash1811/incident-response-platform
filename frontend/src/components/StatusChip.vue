<template>
  <q-chip
    :color="chipColor"
    text-color="white"
    :label="label"
    :dense="dense"
    class="status-chip"
    square
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'open',
  },
  dense: {
    type: Boolean,
    default: false,
  },
})

const statusMap = {
  open: { color: 'negative', label: 'Open' },
  in_progress: { color: 'warning', label: 'In Progress' },
  resolved: { color: 'positive', label: 'Resolved' },
  closed: { color: 'grey-6', label: 'Closed' },
}

const chipColor = computed(() => statusMap[props.status]?.color || 'grey')
const label = computed(() => statusMap[props.status]?.label || props.status)
</script>

<style scoped>
.status-chip {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
}
</style>
