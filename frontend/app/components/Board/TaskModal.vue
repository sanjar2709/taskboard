<template>
	<UIModal :show="!!task" body-class="max-w-[560px]" @close="emit('close')">
		<template #header>
			<span class="text-xs font-medium text-slate-500 inline-flex items-center gap-1.5">
				<Icon name="lucide:columns-3" size="14" />
				{{ columnTitle }}
			</span>
		</template>

		<form v-if="task" class="space-y-4" @submit.prevent="save">
			<UIInput v-model="form.title" label="Title" maxlength="200" required />
			<UIInput v-model="form.description" label="Description" placeholder="Add more details…" multiline />

			<div class="grid sm:grid-cols-2 gap-4">
				<label class="block">
					<span class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Assignee</span>
					<select
						v-model="form.assignee_id"
						class="w-full h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15 dark:border-slate-700 dark:bg-slate-950"
					>
						<option :value="null">Nobody</option>
						<option v-for="member in store.board?.members" :key="member.user.id" :value="member.user.id">
							{{ member.user.full_name || member.user.email }}
						</option>
					</select>
				</label>
				<UIInput v-model="form.due_date" label="Due date" type="date" />
			</div>

			<UIAlert :text="error" />

			<div class="flex items-center justify-between gap-2 pt-2">
				<UIButton variant="ghost" icon="lucide:trash-2" text="Delete" class="!text-red-600" @click="remove" />
				<div class="flex gap-2">
					<UIButton variant="secondary" text="Cancel" @click="emit('close')" />
					<UIButton type="submit" text="Save" :loading="saving" />
				</div>
			</div>
			<p class="text-xs text-slate-400">Created {{ formatDate(task.created_at) }} · updated {{ formatDate(task.updated_at) }}</p>
		</form>
	</UIModal>
</template>

<script lang="ts" setup>
interface Props {
	taskId: number | null
}
const props = defineProps<Props>()

const emit = defineEmits<{ close: [] }>()

const store = useBoardStore()

// Read from the store, so a change made by someone else shows up here too
const task = computed(() => (props.taskId ? store.findTask(props.taskId) : undefined))
const columnTitle = computed(() => (task.value ? store.findColumn(task.value.column_id)?.title : ''))

const form = reactive({ title: '', description: '', assignee_id: null as number | null, due_date: '' })
const saving = ref(false)
const error = ref('')

watch(
	() => props.taskId,
	() => {
		if (!task.value) return
		error.value = ''
		Object.assign(form, {
			title: task.value.title,
			description: task.value.description,
			assignee_id: task.value.assignee?.id ?? null,
			due_date: task.value.due_date ?? ''
		})
	},
	{ immediate: true }
)

// The task was deleted by another member while the modal was open
watch(task, (value) => props.taskId && !value && emit('close'))

async function save() {
	saving.value = true
	error.value = ''
	try {
		await store.updateTask(props.taskId!, { ...form, due_date: form.due_date || null })
		emit('close')
	} catch (e) {
		error.value = errorMessage(e)
	} finally {
		saving.value = false
	}
}

async function remove() {
	if (!confirm('Delete this task?')) return
	await store.deleteTask(props.taskId!)
	emit('close')
}

function formatDate(value: string) {
	return new Date(value).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>
