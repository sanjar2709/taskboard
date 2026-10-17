<template>
	<div class="container py-8">
		<div class="flex items-center justify-between gap-4 mb-6">
			<div>
				<h1 class="text-2xl font-bold">Your boards</h1>
				<p class="text-sm text-slate-500 mt-1">Boards you own or were invited to</p>
			</div>
			<UIButton text="New board" icon="lucide:plus" @click="showCreate = true" />
		</div>

		<div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
			<div v-for="i in 4" :key="i" class="h-32 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
		</div>

		<div v-else-if="boards?.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
			<BoardCard v-for="board in boards" :key="board.id" :board="board" />
		</div>

		<div v-else class="flex flex-col items-center text-center py-20 px-4 rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-800">
			<div class="w-14 h-14 rounded-2xl bg-primary-50 dark:bg-primary-600/15 text-primary-600 flex-center mb-4">
				<Icon name="lucide:kanban" size="28" />
			</div>
			<h2 class="font-semibold text-lg">No boards yet</h2>
			<p class="text-sm text-slate-500 mt-1 mb-5 max-w-sm">Create your first board. It comes with To do, In progress and Done columns.</p>
			<UIButton text="Create a board" icon="lucide:plus" @click="showCreate = true" />
		</div>

		<UIModal :show="showCreate" title="New board" @close="showCreate = false">
			<form class="space-y-4" @submit.prevent="createBoard">
				<UIInput v-model="title" label="Title" placeholder="e.g. Website redesign" maxlength="100" required autofocus />
				<UIAlert :text="error" />
				<div class="flex justify-end gap-2">
					<UIButton variant="ghost" text="Cancel" @click="showCreate = false" />
					<UIButton type="submit" text="Create" :loading="loading" />
				</div>
			</form>
		</UIModal>
	</div>
</template>

<script lang="ts" setup>
import type { Board, BoardListItem } from '~/types'

useHead({ title: 'Boards' })

const { $get, $post, loading } = useApi()

const { data: boards, pending } = useAsyncData('boards', () => $get<BoardListItem[]>('boards'))

const showCreate = ref(false)
const title = ref('')
const error = ref('')

async function createBoard() {
	error.value = ''
	try {
		const board = await $post<Board>('boards', { body: { title: title.value } })
		await navigateTo(`/boards/${board.id}`)
	} catch (e) {
		error.value = errorMessage(e)
	}
}
</script>
