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
					<h1 class="text-xl font-bold truncate">{{ store.board.title }}</h1>
				</div>
				<div class="flex -space-x-2">
					<UIAvatar v-for="member in store.board.members" :key="member.user.id" :name="member.user.full_name || member.user.email" />
				</div>
			</div>

			<div class="flex-1 min-h-0 overflow-x-auto scroll-thin">
				<div class="container h-full pb-6">
					<div class="flex items-start gap-4 h-full">
						<VueDraggable v-model="store.board.columns" handle=".column-handle" :animation="200" ghost-class="task-ghost" class="flex items-start gap-4 h-full" @end="onColumnDrop">
							<BoardColumn v-for="column in store.board.columns" :key="column.id" :column-id="column.id" :data-column-id="column.id" />
						</VueDraggable>
						<BoardAddColumn />
					</div>
				</div>
			</div>
		</template>
	</div>
</template>

<script lang="ts" setup>
import { VueDraggable } from 'vue-draggable-plus'

const route = useRoute()
const store = useBoardStore()

await store.load(Number(route.params.id))

useHead({ title: () => store.board?.title || 'Board' })

function onColumnDrop(event: { item: HTMLElement; newIndex?: number; oldIndex?: number }) {
	if (event.newIndex === event.oldIndex) return
	store.moveColumn(Number(event.item.dataset.columnId), event.newIndex ?? 0)
}
</script>
