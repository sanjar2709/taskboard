<template>
	<div class="w-[290px] shrink-0">
		<form v-if="adding" class="rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 p-2 space-y-2" @submit.prevent="submit">
			<input
				ref="input"
				v-model="title"
				maxlength="100"
				placeholder="Column title"
				class="w-full h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-primary-500 dark:border-slate-700 dark:bg-slate-950"
				@keydown.esc="adding = false"
			/>
			<div class="flex items-center gap-2">
				<UIButton type="submit" size="small" text="Add column" />
				<UIButton variant="ghost" size="small" icon="lucide:x" @click="adding = false" />
			</div>
		</form>
		<button
			v-else
			class="w-full flex items-center gap-2 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 px-4 py-3 text-sm font-medium text-slate-500 hover:border-primary-500 hover:text-primary-600 transition-300 cursor-pointer"
			@click="start"
		>
			<Icon name="lucide:plus" size="16" /> Add column
		</button>
	</div>
</template>

<script lang="ts" setup>
const store = useBoardStore()

const adding = ref(false)
const title = ref('')
const input = ref<HTMLInputElement>()

function start() {
	adding.value = true
	nextTick(() => input.value?.focus())
}

async function submit() {
	const value = title.value.trim()
	if (!value) return
	title.value = ''
	await store.addColumn(value)
	nextTick(() => input.value?.focus())
}
</script>
