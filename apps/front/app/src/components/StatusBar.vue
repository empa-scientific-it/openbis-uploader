<template>
    <div>    
    Connected as {{user}} 
    <button @click='logout'>Logout</button>
    </div>
</template>

<script setup lang="ts">
    import { useUser } from '@/stores/login'
    import {ref} from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    const auth = useUser();
    const user = auth.user;
    const router = useRouter();
    
    async function logout(ev: Event){
      console.log("LOgging out")
      await auth.logout();  
      router.push({"name":'login'});
    } 
</script>