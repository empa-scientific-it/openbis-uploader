
<template>
    <ul id="example-1">
    <li v-for="item in files" :model="files">
        {{ item.name }}
    </li>
    </ul>
</template>


<script setup lang="ts">
import { PropType } from 'vue';
import {FileInfo} from '../models/Files'
const props = defineProps({
    files: [Object] as PropType<FileInfo[]>
})
</script>