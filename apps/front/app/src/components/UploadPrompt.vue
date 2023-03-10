<script setup lang="ts">
    import { declareVariable } from '@babel/types';
    import { PropType, toRefs, toRaw } from 'vue';
    import {FileInfo} from '../models/Files';
    import {OpenbisObjectTypes} from '../models/Tree';
    import {ParserParameters, ParserParameter, parameterObject} from '../models/ParserParameters';
    import { useUser } from '../stores/login';
    import { useOpenbis } from '../stores/openbis';
    import { useFiles } from '../stores/files';
    import {onMounted, ref, toRef} from 'vue';
    import TreeItem from './TreeItem.vue';
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
        show: Boolean,
    })


    interface state {
        selectedType: string,
        selectedParser: string,
        transferError: string| void,
        parserParameterInfo: ParserParameter,
        selectedParams: object
    }

    function initialState(): state{
        return {
        selectedType: '',
        selectedParser: '',
        transferError: null,
        parserParameterInfo: {} as ParserParameter,
        selectedParams: {}
    }
    }

    const state = initialState()
    const formData = ref(state);


    const thisShow = toRef(props, 'show')
    const cancelPrevent = ref(false);
    const emit = defineEmits<{
            (e: 'save'): void
            (e: 'cancel', value: Boolean): void}>()

    async function handleSave(){
        console.log("args", selected.value.name, current.value.code, formData.value.selectedType, (current.value.type as OpenbisObjectTypes),  toRaw(formData.value.selectedParams));
        if(selected?.value && formData.value.selectedParams){
            try{
                cancelPrevent.value = true;
                const saved = await files.transfer(selected.value.name, current.value.identifier, formData.value.selectedType, (current.value.type as OpenbisObjectTypes), formData.value.selectedParser, toRaw(formData.value.selectedParams));
                emit('save')
            }
            catch(e:any){
                formData.value.transferError = e;
                debugger;
            }
        }
    }

    function handleCancel(){
            formData.value = initialState();
            emit('cancel', false);
    
    }

    function handleTransferError(){
        formData.value.transferError = null;
        thisShow.value = !thisShow.value; 
    }

    async function handleParserChange(){
        formData.value.parserParameterInfo = await openbis.getParserParameters(formData.value.selectedParser);
    }
</script>


<template>
    <Transition name="modal">
        <div v-if="show" class="modal-mask">
        <div class="modal-wrapper">
            <div class="modal-container">
            <div class="modal-header">
                <slot name="header">  Save {{selected.name}} to {{current.type}}: {{current.id}}</slot>
            </div>
            <div class="modal-body">
                <slot name="body">
                    <form>
                        <fieldset class="form-group">
                            <legend>General dataset properties</legend>
                            <label for="select-type">Choose a dataset type:</label>
                            <select v-model="formData.selectedType" id="select-type">
                                <option>Select a parser</option>
                                <option v-for="item in datasetTypes" :value="item" :key="item">
                                    {{item}}
                                </option>
                            </select><br>
                            <label for="select-parser">Select a metadata extraction script:</label>
                            <select v-model="formData.selectedParser" id="select-parser" @change="handleParserChange">
                                <option>select a script</option>
                                <option v-for="item in parserTypes" :value="item" :key="item" >
                                    {{item}}
                                </option>
                            </select> 
                        </fieldset><br>
                        <fieldset class="form-group">
                            <legend>Script parameters</legend>
                            <div v-if="formData.parserParameterInfo.properties" v-for="(parameter, key) in formData.parserParameterInfo.properties">
                                <label :for="key">{{key}}</label>
                                <input v-model="formData.selectedParams[key]" :id="key">
                            </div>
                        </fieldset>
                    </form>
                </slot>
            </div>
            <div class="modal-footer">
                <slot name="modal-footer">
                    <slot name="error" v-if="formData.transferError !== null" >
                        {{formData.transferError}}
                    </slot>
                    <button
                        class="modal-default-button"
                        @click="handleSave"
                    >OK</button>
                    <button
                        class="modal-default-button"
                        @click="handleCancel"
                    >Cancel</button>
                </slot>
            </div>
            </div>
        </div>
        </div>
    </Transition>
</template>



<style>
    .modal-mask {
      position: fixed;
      z-index: 9998;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
      display: table;
      transition: opacity 0.3s ease;
    }
    
    .modal-wrapper {
      display: table-cell;
      vertical-align: middle;
    }
    
    .modal-container {
      width: 50%;
      height: 50%;
      margin: 0px auto;
      padding: 20px 30px;
      background-color: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
      transition: all 0.3s ease;
    }
    
    .modal-header h3 {
      margin-top: 0;
      color: #42b983;
    }
    
    .modal-body {
      margin: 20px 0;
      justify-items: center;
    }
    
    .modal-default-button {
      float: right;
    }
    

    
    .modal-enter-from {
      opacity: 0;
    }
    
    .modal-leave-to {
      opacity: 0;
    }
    
    .modal-enter-from .modal-container,
    .modal-leave-to .modal-container {
      -webkit-transform: scale(1.1);
      transform: scale(1.1);
    }

    form {
        display:  inline-block;
        flex-direction: row;
    }
    fieldset {
        margin: 0;
        padding: 0;
        border: 0.1;
        padding-top: 30px; /* leave a space to position for the labels */
    }
    fieldset {display: inline-block; vertical-align: middle;}
    label {
        display: inline-block;
        font-weight: bold;
    }
    </style>

