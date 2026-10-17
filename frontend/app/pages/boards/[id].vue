<template>
	<div class="flex-1 flex flex-col min-h-0">
		<div v-if="store.loading && !store.board" class="flex-1 flex-center text-slate-400">
			<Icon name="lucide:loader-circle" size="28" class="animate-spin" />
		</div>

		<div v-else-if="store.error" class="flex-1 flex flex-col items-center justify-center gap-3 text-center p-6">
			<Icon name="lucide:search-x" size="40" class="text-slate-300" />
			<p class="font-semibold">{{ store.error }}</p>
			<UIButton variant="secondary" text="Back to boards" icon="lucide:arrow-left" @click="navigateTo('/')" />
		</div>

		<template v-else-if="store.board">
			<div class="container w-full flex flex-wrap items-center justify-between gap-3 py-4">
				<div class="flex items-center gap-2 min-w-0">
					<NuxtLink to="/" class="w-8 h-8 rounded-lg flex-center text-slate-400 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-800 transition-300">
						<Icon name="lucide:arrow-left" />
					</NuxtLink>
					<form v-if="editingTitle" @submit.prevent="saveTitle">
						<input
							ref="titleInput"
							v-model="title"
							maxlength="100"
							class="h-9 rounded-lg border border-primary-500 bg-white dark:bg-slate-950 px-2 text-xl font-bold outline-none"
							@blur="saveTitle"
							@keydown.esc="editingTitle = false"
						/>
					</form>
					<h1 v-else class="text-xl font-bold truncate" :class="{ 'cursor-text': store.isOwner }" @dblclick="startEditingTitle">{{ store.board.title }}</h1>
				</div>
				<div class="flex items-center gap-4">
					<span
						class="inline-flex items-center gap-1.5 text-xs font-medium"
						:class="connected ? 'text-emerald-600' : 'text-slate-400'"
						:title="connected ? 'Changes from others show up instantly' : 'Reconnecting…'"
					>
						<span class="w-2 h-2 rounded-full" :class="connected ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'" />
						{{ connected ? 'Live' : 'Offline' }}
					</span>
					<button class="flex -space-x-2 cursor-pointer" title="Members" @click="showMembers = true">
						<UIAvatar v-for="member in store.board.members" :key="member.user.id" :name="member.user.full_name || member.user.email" />
					</button>
					<UIButton variant="secondary" size="small" icon="lucide:user-plus" text="Share" @click="showMembers = true" />
					<UIButton v-if="store.isOwner" variant="ghost" size="small" icon="lucide:trash-2" title="Delete board" @click="deleteBoard" />
				</div>
			</div>

			<div class="flex-1 min-h-0 overflow-x-auto scroll-thin">
				<div class="container h-full pb-6">
					<div class="flex items-start gap-4 h-full">
						<VueDraggable v-model="store.board.columns" handle=".column-handle" :animation="200" ghost-class="task-ghost" class="flex items-start gap-4 h-full" @end="onColumnDrop">
							<BoardColumn v-for="column in store.board.columns" :key="column.id" :column-id="column.id" :data-column-id="column.id" @open-task="openTaskId = $event" />
						</VueDraggable>
						<BoardAddColumn />
					</div>
				</div>
			</div>
		</template>

		<BoardTaskModal :task-id="openTaskId" @close="openTaskId = null" />
		<BoardMembersModal :show="showMembers" @close="showMembers = false" />
	</div>
</template>

<script lang="ts" setup>
import { VueDraggable } from 'vue-draggable-plus'

const route = useRoute()
const store = useBoardStore()

const boardId = Number(route.params.id)
await store.load(boardId)

const { connected } = useBoardSocket(boardId)

useHead({ title: () => store.board?.title || 'Board' })

const openTaskId = ref<number | null>(null)
const showMembers = ref(false)

// Board title, owner only
const editingTitle = ref(false)
const title = ref('')
const titleInput = ref<HTMLInputElement>()

function startEditingTitle() {
	if (!store.isOwner) return
	title.value = store.board!.title
	editingTitle.value = true
	nextTick(() => titleInput.value?.select())
}

async function saveTitle() {
	if (!editingTitle.value) return
	editingTitle.value = false
	const value = title.value.trim()
	if (value && value !== store.board!.title) await store.renameBoard(value)
}

async function deleteBoard() {
	if (!confirm(`Delete "${store.board!.title}" with all its tasks? This can't be undone.`)) return
	await store.deleteBoard()
	await navigateTo('/')
}

function onColumnDrop(event: { item: HTMLElement; newIndex?: number; oldIndex?: number }) {
	if (event.newIndex === event.oldIndex) return
	store.moveColumn(Number(event.item.dataset.columnId), event.newIndex ?? 0)
}
</script>
