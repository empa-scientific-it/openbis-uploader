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
    
    // const selectedType = ref('');
    // const selectedParser = ref('');
    // const transferError = ref(null);
    // const parserParameterInfo = ref({} as ParserParameters)
    // const selectedParams = ref({});
    const props = defineProps({
        treenode: {} as TreeNode,
    })

    // interface state {
    //     selectedType: string,
    //     selectedParser: string,
    //     transferError: string| void,
    //     parserParameterInfo: ParserParameter,
    //     selectedParams: object
    // }

    // function initialState(): state{
    //     return {
    //     selectedType: '',
    //     selectedParser: '',
    //     transferError: null,
    //     parserParameterInfo: {} as ParserParameter,
    //     selectedParams: {}
    // }
    // }

    // const state = initialState()
    // const formData = ref(state);


    // const thisShow = toRef(props, 'show')
    // const cancelPrevent = ref(false);
    // const emit = defineEmits<{
    //         (e: 'save'): void
    //         (e: 'cancel', value: Boolean): void}>()

    // async function handleSave(){
    //     console.log("args", selected.value.name, current.value.code, formData.value.selectedType, (current.value.type as OpenbisObjectTypes),  toRaw(formData.value.selectedParams));
    //     if(selected?.value && formData.value.selectedParams){
    //         try{
    //             cancelPrevent.value = true;
    //             const saved = await files.transfer(selected.value.name, current.value.id, formData.value.selectedType, (current.value.type as OpenbisObjectTypes), formData.value.selectedParser, toRaw(formData.value.selectedParams));
    //             emit('save')
    //         }
    //         catch(e:any){
    //             formData.value.transferError = e;
    //             debugger;
    //         }
    //     }
    // }

    // function handleCancel(){
    //     if (!cancelPrevent.value){
    //         formData.value = initialState();
    //         emit('cancel', false)
    //     }

    // }

    // function handleTransferError(){
    //     formData.value.transferError = null;
    //     thisShow.value = !thisShow.value; 
    // }

    // async function handleParserChange(){
    //     formData.value.parserParameterInfo = await openbis.getParserParameters(formData.value.selectedParser);
    // }
</script>


<template>
    <form>
        <div id="props" v-for="(attr, name) in current.properties" :current="treenode">
            <label>{{name}}</label>
            <input type="text" name="name" v-model="current.properties[name]">
        </div>
 
    </form>
</template> 



<style>

    </style>

