

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
    const storeFiles = ref({'files': [{'name':'a'}, {'name':'b'}]});
    onMounted(
      async () =>{
        await openbis.updateTree();
        await files.getFileList();
        console.log(openbis.tree)
        openbisTree.value = openbis.tree
        //storeFiles.value = {files: files.fileList}
      }
    )
</script>


<template>
  <div id="a">
    <h1>OpenBIS Dataset Uploader</h1>
  </div>
  <div style="width: 100%;overflow:auto;">
    <div style="float:left; width: 50%">
      <!-- <ul>
        <TreeItem class="item" :model="openbisTree"></TreeItem>
      </ul> -->
    </div>
     <div style="float:right; width: 50%">
      <ul><FileList :model="storeFiles"></FileList></ul>
        
     </div>
  </div>

  <status-bar/>
</template>


<style>
.item {
  cursor: pointer;
  line-height: 1.5;
}
.bold {
  font-weight: bold;
}

li {
    display:inline;
    padding: 10px 40px;
}
</style>