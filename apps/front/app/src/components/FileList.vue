<script setup lang="ts">
    import { declareVariable } from '@babel/types';
import { EMPTY_OBJ } from '@vue/shared';
    import { PropType, Ref } from 'vue';
    import {FileInfo} from '../models/Files'
    const props = defineProps({
        files: [Object] as PropType<FileInfo[]>
    })


    const emit = defineEmits<{(event: 'moved', id: string)}>()

    // function startDrag(event: DragEvent, id: string){
    //     event.dataTransfer.dropEffect = 'move'      
    //     event.dataTransfer.effectAllowed = 'move'      
    //     event.dataTransfer.setData('id', id)
    //     emit('moved', id)
    // }

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
            <tr v-for="item in files" :files="files" class="item" draggable=true  @dragover.prevent  @dragenter.prevent  @dragend="$emit('moved', item.name)" @dragstart="$emit('moved', item.name)" :id="item.name">
                <td class="bi bi-file-earmark" :id="item.name"></td>
                <td>{{ item.name }}</td>
                <td>{{ item.created }}</td>
            </tr>
        </tbody>
    </table>
</template>





