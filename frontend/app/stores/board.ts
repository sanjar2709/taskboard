import { defineStore } from 'pinia'

import type { Board, Column, Task } from '~/types'

export const useBoardStore = defineStore('boardStore', {
	state: () => ({
		board: null as Board | null,
		loading: false,
		error: ''
	}),

	getters: {
		findColumn: (state) => (id: number) => state.board?.columns.find((c) => c.id === id),
		findTask: (state) => (id: number) => state.board?.columns.flatMap((c) => c.tasks).find((t) => t.id === id)
	},

	actions: {
		async load(id: number) {
			const { $get } = useApi()
			this.loading = true
			this.error = ''
			try {
				this.board = await $get<Board>(`boards/${id}`)
			} catch (e) {
				this.board = null
				this.error = errorMessage(e, 'Board not found')
			} finally {
				this.loading = false
			}
		},

		/** Something went wrong on the server, take its version of the board. */
		async resync() {
			if (this.board) await this.load(this.board.id)
		},

		async addTask(columnId: number, title: string) {
			const { $post } = useApi()
			const task = await $post<Task>(`columns/${columnId}/tasks`, { body: { title } })
			this.upsertTask(task)
		},

		// The list was already reordered by drag and drop, here we only tell the server
		async moveTask(taskId: number, columnId: number, index: number) {
			const { $post } = useApi()
			try {
				const task = await $post<Task>(`tasks/${taskId}/move`, { body: { column_id: columnId, index } })
				const local = this.findTask(taskId)
				if (local) Object.assign(local, { column_id: task.column_id, position: task.position })
			} catch {
				await this.resync()
			}
		},

		async addColumn(title: string) {
			const { $post } = useApi()
			const column = await $post<Column>(`boards/${this.board!.id}/columns`, { body: { title } })
			this.upsertColumn({ ...column, tasks: [] })
		},

		async renameColumn(columnId: number, title: string) {
			const { $patch } = useApi()
			const column = await $patch<Column>(`columns/${columnId}`, { body: { title } })
			this.upsertColumn(column)
		},

		async moveColumn(columnId: number, index: number) {
			const { $post } = useApi()
			try {
				const column = await $post<Column>(`columns/${columnId}/move`, { body: { index } })
				const local = this.findColumn(columnId)
				if (local) local.position = column.position
			} catch {
				await this.resync()
			}
		},

		async deleteColumn(columnId: number) {
			const { $delete } = useApi()
			await $delete(`columns/${columnId}`)
			this.removeColumn(columnId)
		},

		upsertTask(task: Task) {
			const column = this.findColumn(task.column_id)
			if (!column) return
			const existing = column.tasks.find((t) => t.id === task.id)
			if (existing) {
				Object.assign(existing, task)
			} else {
				column.tasks.push(task)
			}
			column.tasks.sort((a, b) => a.position - b.position)
		},

		upsertColumn(column: Omit<Column, 'tasks'> & { tasks?: Task[] }) {
			if (!this.board) return
			const existing = this.findColumn(column.id)
			if (existing) {
				Object.assign(existing, { ...column, tasks: existing.tasks })
			} else {
				this.board.columns.push({ ...column, tasks: column.tasks ?? [] })
			}
			this.board.columns.sort((a, b) => a.position - b.position)
		},

		removeColumn(columnId: number) {
			if (this.board) this.board.columns = this.board.columns.filter((c) => c.id !== columnId)
		}
	}
})
