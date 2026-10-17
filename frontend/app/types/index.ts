export interface User {
	id: number
	email: string
	full_name: string
	created_at: string
}

export interface TokenPair {
	access: string
	refresh: string
}

export interface Member {
	user: Pick<User, 'id' | 'email' | 'full_name'>
	role: 'owner' | 'member'
	joined_at: string
}

export interface Task {
	id: number
	board_id: number
	column_id: number
	title: string
	description: string
	position: number
	assignee: Member['user'] | null
	due_date: string | null
	created_at: string
	updated_at: string
}

export interface Column {
	id: number
	board_id: number
	title: string
	position: number
	tasks: Task[]
}

export interface BoardListItem {
	id: number
	title: string
	owner_id: number
	created_at: string
}

export interface Board extends BoardListItem {
	members: Member[]
	columns: Column[]
}

export interface ApiError {
	error: {
		code: string
		message: string
		details: { field: string; message: string }[] | null
	}
}
