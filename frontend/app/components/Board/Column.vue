<template>
	<div v-if="column" class="w-[290px] shrink-0 flex flex-col max-h-full rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800">
		<div class="column-handle flex items-center justify-between gap-2 px-3 pt-3 pb-2 cursor-grab active:cursor-grabbing">
			<form v-if="editing" class="flex-1" @submit.prevent="rename">
				<input
					ref="titleInput"
					v-model="title"
					maxlength="100"
					class="w-full h-8 rounded-md border border-primary-500 bg-white dark:bg-slate-950 px-2 text-sm font-semibold outline-none"
					@blur="rename"
					@keydown.esc="editing = false"
				/>
			</form>
			<h3 v-else class="flex items-center gap-2 font-semibold text-sm truncate" @dblclick="startEditing">
				{{ column.title }}
				<span class="text-xs font-medium text-slate-400 bg-slate-200/70 dark:bg-slate-800 rounded-full px-2 py-0.5">{{ column.tasks.length }}</span>
			</h3>

			<div ref="menuRef" class="relative">
				<button
					class="w-7 h-7 rounded-md flex-center text-slate-400 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-800 transition-300 cursor-pointer"
					@click="showMenu = !showMenu"
				>
					<Icon name="lucide:ellipsis" size="18" />
				</button>
				<div v-if="showMenu" class="absolute right-0 mt-1 w-40 z-20 rounded-lg border border-slate-200 bg-white p-1 shadow-lg dark:border-slate-800 dark:bg-slate-900">
					<button class="w-full flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer" @click="startEditing">
						<Icon name="lucide:pencil" size="14" /> Rename
					</button>
					<button class="w-full flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 cursor-pointer" @click="remove">
						<Icon name="lucide:trash-2" size="14" /> Delete
					</button>
				</div>
			</div>
		</div>

		<VueDraggable
			v-model="column.tasks"
			:data-column-id="column.id"
			group="tasks"
			:animation="150"
			ghost-class="task-ghost"
			drag-class="task-drag"
			class="flex-1 min-h-10 overflow-y-auto scroll-thin px-2 pb-2 space-y-2"
			@end="onTaskDrop"
		>
			<BoardTaskCard v-for="task in column.tasks" :key="task.id" :task="task" @click="emit('open-task', task.id)" />
		</VueDraggable>

		<div class="px-2 pb-2">
			<form v-if="adding" class="space-y-2" @submit.prevent="addTask">
				<textarea
					ref="taskInput"
					v-model="newTask"
					rows="2"
					maxlength="200"
					placeholder="What needs to be done?"
					class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-primary-500 dark:border-slate-700 dark:bg-slate-950 resize-none"
					@keydown.enter.exact.prevent="addTask"
					@keydown.esc="adding = false"
				/>
				<div class="flex items-center gap-2">
					<UIButton type="submit" size="small" text="Add task" />
					<UIButton variant="ghost" size="small" icon="lucide:x" @click="adding = false" />
				</div>
			</form>
			<button
				v-else
				class="w-full flex items-center gap-2 rounded-lg px-2 py-2 text-sm text-slate-500 hover:bg-slate-200/70 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200 transition-300 cursor-pointer"
				@click="startAdding"
			>
				<Icon name="lucide:plus" size="16" /> Add a task
			</button>
		</div>
	</div>
</template>

<script lang="ts" setup>
import { VueDraggable } from 'vue-draggable-plus'

interface Props {
	columnId: number
}
const props = defineProps<Props>()

const emit = defineEmits<{ 'open-task': [id: number] }>()

const store = useBoardStore()
// Columns live in the store, so drag and drop and live updates change the same object
const column = computed(() => store.findColumn(props.columnId)!)

// Menu
const showMenu = ref(false)
const menuRef = ref<HTMLElement>()
onClickOutside(menuRef, () => (showMenu.value = false))

// Rename
const editing = ref(false)
const title = ref('')
const titleInput = ref<HTMLInputElement>()

function startEditing() {
	showMenu.value = false
	title.value = column.value.title
	editing.value = true
	nextTick(() => titleInput.value?.select())
}

async function rename() {
	if (!editing.value) return
	editing.value = false
	const value = title.value.trim()
	if (value && value !== column.value.title) await store.renameColumn(column.value.id, value)
}

async function remove() {
	showMenu.value = false
	const tasks = column.value.tasks.length
	if (tasks && !confirm(`Delete "${column.value.title}" with ${tasks} task${tasks > 1 ? 's' : ''}?`)) return
	await store.deleteColumn(column.value.id)
}

// New task
const adding = ref(false)
const newTask = ref('')
const taskInput = ref<HTMLTextAreaElement>()

function startAdding() {
	adding.value = true
	nextTick(() => taskInput.value?.focus())
}

async function addTask() {
	const value = newTask.value.trim()
	if (!value) return
	newTask.value = ''
	await store.addTask(column.value.id, value)
	nextTick(() => taskInput.value?.focus())
}

// Drag and drop: the list is already updated, send the new place to the server
function onTaskDrop(event: { item: HTMLElement; to: HTMLElement; from: HTMLElement; newIndex?: number; oldIndex?: number }) {
	if (event.from === event.to && event.newIndex === event.oldIndex) return
	const taskId = Number(event.item.dataset.taskId)
	const columnId = Number(event.to.dataset.columnId)
	store.moveTask(taskId, columnId, event.newIndex ?? 0)
}
</script>
