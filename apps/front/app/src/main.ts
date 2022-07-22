
import App from '@/App.vue'
import {createApp, markRaw } from 'vue'
import piniaInstance from '@/stores/store'
import {router} from "@/helpers/router"

const app = createApp(App).use(piniaInstance).use(router).mount('#app');
