
<template>
    <router-view />
</template>

<script setup lang="ts">
  import {useUser} from "@/stores/login";
  import {onBeforeMount} from 'vue';
  console.log("App")
  onBeforeMount( async () => {
    const store = useUser();
    await store.init();
    console.log(store)
})
 
</script>


<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
