<template>
  <div id="a">
     <h1>OpenBIS Dataset Uploader</h1>
     <h2>Logged in as {{ user }}</h2>
  </div>
</template>


<script setup lang="ts">
    import { useUser } from '@/stores/login'
    import {ref} from 'vue'
    const auth = useUser();
    const user = auth.user;
</script>