<script setup lang="ts">
    import { declareVariable } from '@babel/types';
    import { PropType } from 'vue';
    import {FileInfo} from '../models/Files'
    const props = defineProps({
        files: [Object] as PropType<FileInfo[]>
    })


    function startDrag(evt: DragEvent, item: FileInfo){
        evt.dataTransfer.dropEffect = 'move'      
        evt.dataTransfer.effectAllowed = 'move'      
        evt.dataTransfer.setData('id', item.name)
        console.log(evt.dataTransfer.files)
    }

</script>


<template>
    <table id="files" class="table table-striped table-bordered">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Created</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="item in files" :files="files" class="item" draggable=true  @dragstart="startDrag($event, item)" :id="item.name">
                <td class="bi bi-file-earmark" :id="item.name"></td>
                <td>{{ item.name }}</td>
                <td>{{ item.created }}</td>
            </tr>
        </tbody>
    </table>
</template>





