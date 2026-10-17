import type { BoardEvent } from '~/types'

/**
 * Live updates for one board. Reconnects with a growing delay when the connection drops.
 * Every time the socket opens the board is loaded again: anything that changed before the
 * connection was ready (or while it was down) never comes as an event.
 */
export const useBoardSocket = (boardId: number) => {
	const config = useRuntimeConfig()
	const auth = useAuthStore()
	const store = useBoardStore()

	const connected = ref(false)
	let socket: WebSocket | null = null
	let retries = 0
	let reconnectTimer: ReturnType<typeof setTimeout> | undefined
	let stopped = false

	// Proxies close idle connections, a small ping every 25 seconds keeps it open
	const { pause: stopPing, resume: startPing } = useIntervalFn(() => socket?.send('ping'), 25_000, { immediate: false })

	async function connect() {
		// The token may have expired while the tab was in the background
		if (retries > 0) await auth.refreshTokens()

		socket = new WebSocket(`${config.public.wsBaseUrl}boards/${boardId}/ws?token=${auth.access}`)

		socket.onopen = () => {
			store.resync()
			connected.value = true
			retries = 0
			startPing()
		}

		socket.onmessage = ({ data }) => {
			if (data === 'pong') return
			const message: BoardEvent = JSON.parse(data)
			if (message.event === 'board.deleted') {
				navigateTo('/')
				return
			}
			if (message.event === 'member.removed' && message.data.user_id === auth.user?.id) {
				navigateTo('/')
				return
			}
			store.applyEvent(message)
		}

		socket.onclose = () => {
			connected.value = false
			stopPing()
			if (stopped) return
			retries += 1
			reconnectTimer = setTimeout(connect, Math.min(1000 * 2 ** retries, 30_000))
		}
	}

	function disconnect() {
		stopped = true
		clearTimeout(reconnectTimer)
		socket?.close()
	}

	onMounted(connect)
	onBeforeUnmount(disconnect)

	return { connected }
}
