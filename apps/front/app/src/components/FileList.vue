<script setup lang="ts">
    import { declareVariable } from '@babel/types';
    import { EMPTY_OBJ } from '@vue/shared';
    import { PropType, Ref } from 'vue';
    import {FileInfo} from '../models/Files'
    import FileList from './FileList.vue'
    import { storeToRefs } from 'pinia';
    import { useFiles } from '../stores/files';

   
    const ds = useFiles();
    const {fileList, selected} = storeToRefs(ds);

    const emit = defineEmits<{
        (event: 'moved', id: string),
        (event: 'dropped', file: DataTransfer)
    }>()

    function handleFileMoved(item){
        selected.value = item;
        emit('moved', item.name);
    }

    function handleFileDropped(ev: DragEvent){
        console.log(ev.dataTransfer.files[0])
        emit('dropped', ev.dataTransfer)
    }
</script>


<template>
    <div class="fixedhead" @drop.prevent="handleFileDropped"  @dragover.prevent  @dragenter.prevent>
        <table id="files" class="table table-striped table-bordered">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Created</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="item in fileList" class="item" draggable=true  @dragover.prevent  @dragenter.prevent  @dragend="handleFileMoved(item)" @dragstart="handleFileMoved(item)" :id="item.name">
                <td class="bi bi-file-earmark" :id="item.name" @click="selected.value=item"></td>
                <td>{{ item.name }}</td>
                <td>{{ item.created }}</td>
            </tr>
        </tbody>
    </table>
    </div>

</template>



<style>
     .fixedhead {
        overflow-y:auto;
        height: 100%;
    }
    .fixedhead thead tr th {
      position: sticky;
      top: 0;
      fill: white;
      background: white;
    }


    table {
      border-collapse: collapse;        
      width: 100%;
      text-align: left;
    }


</style>

