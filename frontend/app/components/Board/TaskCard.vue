<template>
	<div
		:data-task-id="task.id"
		class="group rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-3 shadow-sm hover:border-primary-500/60 hover:shadow transition-300 cursor-grab active:cursor-grabbing"
	>
		<p class="text-sm font-medium leading-snug break-words">{{ task.title }}</p>

		<div v-if="task.description || task.due_date || task.assignee" class="flex items-center justify-between gap-2 mt-2.5">
			<div class="flex items-center gap-2 text-xs text-slate-500">
				<span
					v-if="task.due_date"
					class="inline-flex items-center gap-1 rounded px-1.5 py-0.5"
					:class="isOverdue ? 'bg-red-50 text-red-600 dark:bg-red-950/50 dark:text-red-400' : 'bg-slate-100 dark:bg-slate-700/60'"
				>
					<Icon name="lucide:calendar" size="12" />
					{{ dueLabel }}
				</span>
				<Icon v-if="task.description" name="lucide:align-left" size="14" title="Has description" />
			</div>
			<UIAvatar v-if="task.assignee" :name="task.assignee.full_name || task.assignee.email" size="small" />
		</div>
	</div>
</template>

<script lang="ts" setup>
import type { Task } from '~/types'

interface Props {
	task: Task
}
const props = defineProps<Props>()

const isOverdue = computed(() => !!props.task.due_date && new Date(props.task.due_date) < new Date(new Date().toDateString()))
const dueLabel = computed(() => (props.task.due_date ? new Date(props.task.due_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : ''))
</script>
