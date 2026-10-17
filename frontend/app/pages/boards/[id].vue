<template>
	<div class="container py-8">
		<h1 class="text-2xl font-bold">{{ board?.title }}</h1>
	</div>
</template>

<script lang="ts" setup>
import type { Board } from '~/types'

const route = useRoute()
const { $get } = useApi()

const { data: board } = useAsyncData(`board-${route.params.id}`, () => $get<Board>(`boards/${route.params.id}`))

useHead({ title: () => board.value?.title || 'Board' })
</script>
