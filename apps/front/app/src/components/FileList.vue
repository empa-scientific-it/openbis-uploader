<template>
    <ul id="example-1">
    <li v-for="item in items" :key="item.message">
        {{ item.message }}
    </li>
    </ul>
</template>


<script setup lang="ts">
    import { useUser } from '@/stores/login'
    import { useFile } from '@/stores/files'
    const auth = useUser();
    const user = auth.user;
</script>