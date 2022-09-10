<script setup lang="ts">
    import { declareVariable } from '@babel/types';
    import { PropType } from 'vue';
    import {FileInfo} from '../models/Files'
    import {OpenbisObjectTypes} from '../models/Tree'
    import { useUser } from '../stores/login';
    import { useOpenbis } from '../stores/openbis';
    import { useFiles } from '../stores/files';
    import {onMounted, ref} from 'vue';
    import TreeItem from './TreeItem.vue'
    import FileList from './FileList.vue'
    import {storeToRefs} from 'pinia';
    import {DropBox} from '../services/DropBox'

    const openbis = useOpenbis();
    const files = useFiles();
    const {tree, current, datasetTypes} = storeToRefs(openbis);
    const {fileList, selected} = storeToRefs(files);
    
    const selectedType = ref('');
    const transferError = ref(null);
    const props = defineProps({
        show: Boolean,
    })

    onMounted(
        async () => {
            const dsTypes= await openbis.getDatasetTypes()
        }
    )
    const emit = defineEmits<{
            (e: 'save'): void
            (e: 'cancel', value: Boolean): void}>()

    async function handleSave(){
        debugger
        console.log(selected.value, current.value, selectedType.value)
        if(selected?.value){
            try{
                await files.transfer(selected.value.name, current.value.id, selectedType.value, (current.value.type as OpenbisObjectTypes))
                emit('save')
            }
            catch(e:any){
                debugger
                transferError.value = e;
            }
        }
    }
</script>


<template>
    <Transition name="modal">
        <div v-if="show" class="modal-mask">
        <div class="modal-wrapper">
            <div class="modal-container">
            <div class="modal-header">
              
                <slot name="header">  Save {{selected.name}} to {{current.id}}</slot>
            </div>

            <div class="modal-body">
                <slot name="error" v-if="transferError !== null">
                    {{transferError}}
                </slot>
                <slot name="body">
                   <select v-model="selectedType">
                    <option v-for="item in datasetTypes" :value="item" :key="item">
                        {{item}}
                    </option>
                   </select> 
                </slot>
            </div>

            <div class="modal-footer">
                <slot name="footer">
                default footer
                <button
                    class="modal-default-button"
                    @click="handleSave"
                >OK</button>
                <button
                    class="modal-default-button"
                    @click="$emit('cancel')"
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
      width: 300px;
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
    }
    
    .modal-default-button {
      float: right;
    }
    
    /*
     * The following styles are auto-applied to elements with
     * transition="modal" when their visibility is toggled
     * by Vue.js.
     *
     * You can easily play with the modal transition by editing
     * these styles.
     */
    
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
    </style>

