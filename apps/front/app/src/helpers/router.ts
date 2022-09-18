import {useUser} from "@/stores/login"
import {createRouter, createWebHistory ,  RouteRecordRaw } from 'vue-router'
import { storeToRefs } from "pinia";
import { objectToString } from "@vue/shared";

const routes: Array<RouteRecordRaw> = [
  { 
      path: '/eln', name:"eln",  component: () => import('@/components/StartPage.vue'),  meta: { requiresAuth: true}
  },
  {
      path: '/login', name: "login", component:  () => import('@/components/OpenBisLogin.vue'), meta: { requiresAuth: false}
  },
  {
      path: '/', component:  () => import('@/components/StartPage.vue'), meta: { requiresAuth: true}
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
});




// Routing guard redirecting to login
// if the user is not logged
router.beforeEach((to, from) => {
  const store = useUser();
  const {user, sessionToken, loggedIn} = storeToRefs(store)
  debugger
  if (((to.matched.some((record) => record.meta.requiresAuth)) && !loggedIn.value) && to.name != "login"){
      return {name: "login"}
  }
}
);


export {router};