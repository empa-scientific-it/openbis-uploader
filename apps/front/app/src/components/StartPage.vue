

<script setup lang="ts">
    import StatusBar from './StatusBar.vue';
    import { useUser } from '../stores/login';
    import { useOpenbis } from '../stores/openbis';
    import { useFiles } from '../stores/files';
    import {onMounted, ref, watch, onBeforeMount} from 'vue';
    import {storeToRefs} from 'pinia';
    import TreeItem from './TreeItem.vue'
    import FileList from './FileList.vue'
    import UploadPrompt from './UploadPrompt.vue';

    const auth = useUser();
    const user = auth.user;
    const openbis = useOpenbis();
    const files = useFiles();
    const {tree, current, datasetTypes} = storeToRefs(openbis);
    const {fileList, selected} = storeToRefs(useFiles());
    
    const showPopup = ref(false);



    function allowDrop(event){
      console.log(event)
    };

    // async function dropFile(event: DropEvent){
    //   debugger
    //   const fileId = event.dataTransfer.getData('id')

    //   showPopup.value = true;
    //   console.log(`transfer ${fileId} to ${targetId}`);
    //   console.log(showPopup.value)
    //   //await files.transfer(fileId, targetId);
    // };
    onBeforeMount(
      async () => {
        await openbis.init()
      }
    );
    onMounted(
      async () =>{
        await openbis.updateTree();
        await files.getFileList();
      }
    )

    function selectOpenbisElement(event){
    }

    function handleFileMoved(source){   
      console.log(`Moved file ${source}`)
      selected.value = source
    }

    async function handleFileDropped(dest){
      console.log(`Dropped ${selected.value} on ${dest}`)
      if(selected.value){
        try{
          await files.transfer(selected.value, dest)
        } catch(e) {
          console.log(e);
          alert(e)
        }
      }
    }

</script>


<template>
<div class="grid-container">
    <div id="a" class="header">
      <h1>OpenBIS Dataset Uploader</h1>
    </div>
    <div class="menu">
      <h1>Openbis Tree</h1>
      <ul>
        <TreeItem class="item" :model="tree" @dropped="handleFileDropped"></TreeItem>
      </ul>
    </div>
    <div class="main">
      <h1>Files on Datastore</h1>
      <FileList :files="fileList" @moved="handleFileMoved"></FileList>
    </div>
  <div id="a" class="foot"><status-bar/></div>
  <UploadPrompt :show="showPopup"></UploadPrompt>
</div>
</template>


<style>

.item {
  cursor: pointer;
  line-height: 1.5;
}


.header { display: grid-item; grid-area: header; }
.menu { display: grid-item; grid-area: menu; justify-items: left; }
.main { display: grid-item; grid-area: main; }
.right {display: grid-item; grid-area: right; }
.foot { display: grid-item; grid-area: footer; }
grid-item {
  display: flex;            /* new */
  align-items: left;      /* new */
  justify-items: left;    /* new */
}
.grid-container {
  display: grid;
  grid-template-areas:
    'header header header header header header'
    'menu menu main main right right'
    'footer footer footer footer footer footer';
  gap: 10px;
  background-color: #FFFF;
  padding: 10px;
}



</style>