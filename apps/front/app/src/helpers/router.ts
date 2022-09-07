import {useUser, existingSession} from "@/stores/login"
import {createRouter, createWebHistory ,  RouteRecordRaw } from 'vue-router'


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
  console.log(store.loggedIn)
  if (((to.matched.some((record) => record.meta.requiresAuth)) && !store.loggedIn) && to.name != "login"){
      return {name: "login"}
  }
});


export {router};