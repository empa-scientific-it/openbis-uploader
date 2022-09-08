
import App from '@/App.vue'
import {createApp, markRaw } from 'vue'
import piniaInstance from '@/stores/store'
import {router} from "@/helpers/router"
import 'bootstrap-icons/font/bootstrap-icons.css'

const app = createApp(App).use(piniaInstance).use(router).mount('#app');
