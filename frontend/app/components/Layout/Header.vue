<template>
	<header class="h-14 shrink-0 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80 sticky top-0 z-30">
		<div class="container h-full flex items-center justify-between gap-4">
			<NuxtLink to="/" class="flex items-center gap-2 font-bold text-lg">
				<img src="/favicon.svg" alt="" class="w-7 h-7" />
				<span>Taskboard</span>
			</NuxtLink>

			<div class="flex items-center gap-2">
				<button
					class="w-9 h-9 rounded-lg flex-center text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-100 transition-300 cursor-pointer"
					:title="isDark ? 'Light mode' : 'Dark mode'"
					@click="toggleDark()"
				>
					<Icon :name="isDark ? 'lucide:sun' : 'lucide:moon'" />
				</button>
			</div>
		</div>
	</header>
</template>

<script lang="ts" setup>
const isDark = useDark()
const toggleDark = useToggle(isDark)
</script>
