import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
	compatibilityDate: '2025-07-15',
	devtools: { enabled: true },
	// Dashboard behind a login, nothing to index, so a plain SPA is enough
	ssr: false,

	app: {
		head: {
			title: 'Taskboard',
			titleTemplate: '%s · Taskboard',
			htmlAttrs: { lang: 'en' },
			link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }]
		}
	},

	css: ['~/assets/css/main.css'],

	modules: [
		'@vueuse/nuxt',
		[
			'@pinia/nuxt',
			{
				autoImports: ['defineStore', ['defineStore', 'definePiniaStore']]
			}
		],
		'@nuxt/icon',
		'@nuxt/eslint'
	],
	vite: {
		plugins: [tailwindcss()]
	},
	icon: {
		size: '20px',
		serverBundle: {
			collections: ['lucide']
		}
	},
	runtimeConfig: {
		public: {
			apiBaseUrl: 'http://localhost:8002/api/v1/',
			wsBaseUrl: 'ws://localhost:8002/api/v1/'
		}
	}
})
