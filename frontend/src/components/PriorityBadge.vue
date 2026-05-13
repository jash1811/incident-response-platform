<template>
  <q-badge
    :color="badgeColor"
    :label="label"
    class="priority-badge"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  priority: {
    type: String,
    default: 'medium',
  },
})

const priorityMap = {
  low: { color: 'positive', label: 'Low' },
  medium: { color: 'warning', label: 'Medium' },
  high: { color: 'orange', label: 'High' },
  critical: { color: 'negative', label: 'Critical' },
}

const badgeColor = computed(() => priorityMap[props.priority]?.color || 'grey')
const label = computed(() => priorityMap[props.priority]?.label || props.priority)
</script>

<style scoped>
.priority-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
}
</style>
