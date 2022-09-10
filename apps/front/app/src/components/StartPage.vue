

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
      console.log(selected.value)
    }

    async function handleFileDropped(dest){
      console.log(`Dropped ${selected.value} on ${current.value}`)
      if(selected.value){
        showPopup.value = true;
      }
    }

    async function handleTransfer(){
      console.log(`${selected.value} to ${current.value}`)
      showPopup.value = !showPopup.value;
    }
    function handleCancel(ev){
      showPopup.value = !showPopup.value;
    }

</script>


<template>
<div class="grid-container">
    <div id="a" class="header"><status-bar/></div>
    <div class="title">
      <h1>OpenBIS Dataset Uploader</h1>
    </div>
    <div class="menu">
      <h2>Openbis Tree</h2>
      <ul>
        <TreeItem class="item" :model="tree" @dropped="handleFileDropped"></TreeItem>
      </ul>
    </div>
    <div class="main">
      <h2>Files on Datastore</h2>
      <FileList @moved="handleFileMoved"></FileList>
    </div>
  <UploadPrompt :show="showPopup" @cancel="handleCancel" @save="handleTransfer" :file="selected" :dest="current"></UploadPrompt>
</div>
</template>


<style>

.main .tbody {
        overflow-y:auto;
        height: 50%;
    }

.menu ul  {
        overflow-y:auto;
        height: 50%;
    }


.item {
  cursor: pointer;
  line-height: 1.5;
}


.grid-container {
  display: grid;
  grid-template-areas:
    'header header header'
    'title title title' 
    'menu main right '
    'footer main right';
  gap: 2%;
  background-color: #FFFF;
  padding: 1%;
}

grid-item {
  display: grid;            /* new */
  align-items: left;      /* new */
  justify-items: left;    /* new */
  align-self: stretch;
}

.header { display: grid-item; grid-area: header; justify-content: start; }
.title {display: grid-item; grid-area: title;}
.menu { display: grid-item; grid-area: menu;}
.main { display: grid-item; grid-area: main;}
.right {display: grid-item; grid-area: right;}
.foot { display: grid-item; grid-area: footer;}

</style>