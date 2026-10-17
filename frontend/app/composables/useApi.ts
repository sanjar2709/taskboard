import type { FetchOptions } from 'ofetch'

export const useApi = () => {
	const config = useRuntimeConfig()
	const loading = ref(false)

	function $service(options?: FetchOptions) {
		return $fetch.create({
			...options,
			baseURL: config.public.apiBaseUrl
		})
	}

	function request<T>(endpoint: string, options?: FetchOptions): Promise<T> {
		loading.value = true
		return $service(options)<T>(endpoint).finally(() => {
			loading.value = false
		}) as Promise<T>
	}

	const $get = <T = never>(endpoint: string, options?: FetchOptions) => request<T>(endpoint, { ...options, method: 'GET' })
	const $post = <T = never>(endpoint: string, options?: FetchOptions) => request<T>(endpoint, { ...options, method: 'POST' })
	const $patch = <T = never>(endpoint: string, options?: FetchOptions) => request<T>(endpoint, { ...options, method: 'PATCH' })
	const $delete = <T = never>(endpoint: string, options?: FetchOptions) => request<T>(endpoint, { ...options, method: 'DELETE' })

	return { loading, $get, $post, $patch, $delete }
}
