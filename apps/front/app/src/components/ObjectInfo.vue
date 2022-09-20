<script setup lang="ts">
    import { declareVariable } from '@babel/types';
    import { PropType, toRefs, toRaw } from 'vue';
    import {FileInfo} from '../models/Files';
    import {OpenbisObjectTypes, TreeNode} from '../models/Tree';
    import {ParserParameters, ParserParameter, parameterObject} from '../models/ParserParameters';
    import { useUser } from '../stores/login';
    import { useOpenbis } from '../stores/openbis';
    import { useFiles } from '../stores/files';
    import {onMounted, ref, toRef} from 'vue';
    import FileList from './FileList.vue';
    import {storeToRefs} from 'pinia';
    import {DropBox} from '../services/DropBox';

    const openbis = useOpenbis();
    const files = useFiles();
    const {tree, current, datasetTypes, parserTypes} = storeToRefs(openbis);
    const {fileList, selected} = storeToRefs(files);
    

    const props = defineProps({
        treenode: {} as TreeNode,
    })

   
</script>


<template>
    <form>
        <fieldset>
            <legend>Object properties</legend>
            <div id="props" v-for="(attr, name) in current.properties" :current="treenode">
                <label>{{name}}</label>
                <input type="text" name="name" v-model="current.properties[name]">
            </div>
        </fieldset>
        <fieldset>
            <legend>Relationships</legend>
            <div id="props" v-for="name in current.ancestors" :current="treenode">
                <textarea>{{name}}</textarea>
            </div>
        </fieldset>

 
    </form>
</template> 



<style>
    form {
        display:  grid;
        flex-direction: row;
    }
</style>

