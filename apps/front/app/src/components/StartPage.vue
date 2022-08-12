<template>
  <div id="a">
     <h1>OpenBIS Dataset Uploader</h1>
  </div>
  <status-bar/>
</template>


<script setup lang="ts">
    import StatusBar from './StatusBar.vue';
    import { useUser } from '@/stores/login';
    import {ref} from 'vue';
    const auth = useUser();
    const user = auth.user;
</script>