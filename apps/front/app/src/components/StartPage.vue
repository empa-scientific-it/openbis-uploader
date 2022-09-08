

<script setup lang="ts">
    import StatusBar from './StatusBar.vue';
    import { useUser } from '../stores/login';
    import { useOpenbis } from '../stores/openbis';
    import { useFiles } from '../stores/files';
    import {onMounted, ref} from 'vue';
    import TreeItem from './TreeItem.vue'
    import FileList from './FileList.vue'

    const auth = useUser();
    const user = auth.user;
    const openbis = useOpenbis();
    const files = useFiles();
    const openbisTree = ref({'id':'a'});
    const storeFiles = ref([{'name':'a'}, {'name':'b'}]);

    function allowDrop(event){
      console.log(event)
    };

    async function dropFile(event: DropEvent, target: TreeItem){
      const fileId = event.dataTransfer.getData('id')
      const targetId = target.id;
      console.log(`transfer ${fileId} to ${targetId}`);
      await files.transfer(fileId, targetId);
    };

    onMounted(
      async () =>{
        await openbis.updateTree();
        await files.getFileList();
        console.log(openbis.tree)
        openbisTree.value = openbis.tree
        storeFiles.value = files.fileList
      }
    )

</script>


<template>
<div class="grid-container">
    <div id="a" class="header">
      <h1>OpenBIS Dataset Uploader</h1>
    </div>
    <div class="menu">
      <h1>Openbis Tree</h1>
      <ul>
        <TreeItem class="item" :model="openbisTree"    @dragover.prevent  @dragenter.prevent @drop.prevent="dropFile($event, openbisTree)"></TreeItem>
      </ul>
    </div>
    <div class="main">
      <h1>Files on Datastore</h1>
      <FileList :files="storeFiles"></FileList>
    </div>
  <div id="a" class="foot"><status-bar/></div>
</div>
</template>


<style>

grid-item {
  display: flex;            /* new */
  align-items: center;      /* new */
  justify-items: center;    /* new */
}

.header { display: grid-item; grid-area: header; }
.menu { display: grid-item; grid-area: menu; }
.main { display: grid-item; grid-area: main; }
.right {display: grid-item; grid-area: right; }
.foot { display: grid-item; grid-area: footer; }

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