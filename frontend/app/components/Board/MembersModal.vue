<template>
	<UIModal :show="show" title="Board members" @close="emit('close')">
		<form v-if="store.isOwner" class="flex gap-2 mb-5" @submit.prevent="invite">
			<UIInput v-model="email" type="email" placeholder="Email of a registered user" class="flex-1" required />
			<UIButton type="submit" text="Invite" icon="lucide:user-plus" :loading="inviting" />
		</form>
		<UIAlert :text="error" class="mb-4" />

		<ul class="divide-y divide-slate-100 dark:divide-slate-800">
			<li v-for="member in store.board?.members" :key="member.user.id" class="flex items-center gap-3 py-2.5">
				<UIAvatar :name="member.user.full_name || member.user.email" />
				<div class="flex-1 min-w-0">
					<p class="text-sm font-medium truncate">{{ member.user.full_name || member.user.email }}</p>
					<p class="text-xs text-slate-500 truncate">{{ member.user.email }}</p>
				</div>
				<span v-if="member.role === 'owner'" class="text-xs font-medium text-primary-600 bg-primary-50 dark:bg-primary-600/15 rounded-full px-2 py-0.5">Owner</span>
				<button
					v-else-if="store.isOwner"
					class="w-8 h-8 rounded-lg flex-center text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 transition-300 cursor-pointer"
					title="Remove from board"
					@click="remove(member.user.id)"
				>
					<Icon name="lucide:user-minus" size="16" />
				</button>
			</li>
		</ul>
	</UIModal>
</template>

<script lang="ts" setup>
defineProps<{ show: boolean }>()
const emit = defineEmits<{ close: [] }>()

const store = useBoardStore()

const email = ref('')
const inviting = ref(false)
const error = ref('')

async function invite() {
	inviting.value = true
	error.value = ''
	try {
		await store.addMember(email.value)
		email.value = ''
	} catch (e) {
		error.value = errorMessage(e)
	} finally {
		inviting.value = false
	}
}

async function remove(userId: number) {
	error.value = ''
	try {
		await store.removeMember(userId)
	} catch (e) {
		error.value = errorMessage(e)
	}
}
</script>
