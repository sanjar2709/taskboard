<template>
	<NuxtLink
		:to="`/boards/${board.id}`"
		class="group relative flex flex-col justify-between h-32 rounded-xl p-4 text-white overflow-hidden shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-300"
		:class="gradients[board.id % gradients.length]"
	>
		<h3 class="font-semibold text-lg leading-tight line-clamp-2">{{ board.title }}</h3>
		<div class="flex items-center justify-between text-xs text-white/80">
			<span>{{ isOwner ? 'Owner' : 'Member' }}</span>
			<span>{{ created }}</span>
		</div>
		<Icon name="lucide:kanban" class="absolute -right-3 -bottom-3 text-white/15 group-hover:scale-110 transition-300" size="72" />
	</NuxtLink>
</template>

<script lang="ts" setup>
import type { BoardListItem } from '~/types'

interface Props {
	board: BoardListItem
}
const props = defineProps<Props>()

const auth = useAuthStore()

const gradients = [
	'bg-gradient-to-br from-indigo-500 to-violet-600',
	'bg-gradient-to-br from-sky-500 to-cyan-600',
	'bg-gradient-to-br from-emerald-500 to-teal-600',
	'bg-gradient-to-br from-rose-500 to-pink-600',
	'bg-gradient-to-br from-amber-500 to-orange-600'
]

const isOwner = computed(() => props.board.owner_id === auth.user?.id)
const created = computed(() => new Date(props.board.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }))
</script>
