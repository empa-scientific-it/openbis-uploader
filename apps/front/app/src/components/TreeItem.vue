<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { TreeNode } from '../models/Tree'
  import { PropType } from 'vue';
  import { useOpenbis } from '../stores/openbis';
  import { storeToRefs } from 'pinia';
  import { propsToAttrMap } from '@vue/shared';

  const props = defineProps({
      model: Object as PropType<TreeNode>,
      handleDrop: Function
  })

  const openbis = useOpenbis();
  const {tree, current, datasetTypes} = storeToRefs(openbis);


  const isOpen = ref(false)
  const isFolder = computed(() => {
  return props.model.children && props.model.children.length
  })

  const itemIcon = computed(() => {
    console.log(isOpen.value)
    switch(props.model.type){
        case "SPACE": return  (isOpen.value ? "bi bi-folder2-open" : 'bi bi-folder2')
        case "INSTANCE": return (isOpen.value ? "bi bi-folder2-open" : 'bi bi-folder2')
        case "PROJECT": return (isOpen.value ? "bi bi-folder2-open" : 'bi bi-folder2')
        case "COLLECTION": return "bi bi-table"
        case "OBJECT": return "bi bi-card-list"
    }
    }
    );

  function toggle() {
    isOpen.value = !isOpen.value
    current.value = props.model;
    console.log(current.value);
  }

  const emit = defineEmits<{(event: 'dropped', target: string): void }>();

  function handleDrop(event){
    console.log(event.dataTransfer.getData('id'))
    console.log(`Handler Currently in ${props.model.id}`);
    current.value = props.model;
    emit('dropped', props.model.id);
  }
  // This just reemits the event all over the tree
  function handleDropped(level){
  console.log(`Dropped Handler Currently in ${props.model.id} ${level}`);
  emit('dropped', level)
  }

</script>




<template>
  <li class="tree" @dragover.prevent @dragenter.prevent>
        <div class="node" @click="toggle"  @drop="handleDrop" @dragover.prevent @dragenter.prevent> 
            <span><i :class="itemIcon"></i></span>
            <a>{{ model.code }}</a>
        </div>
    <ul v-show="isOpen" v-if="isFolder" >
      <TreeItem class="tree" v-for="model in model.children" :model="model" @dropped="handleDropped">
      </TreeItem>
    </ul>
  </li>
</template>

<style>

.tree{
  
  text-align: left;

}

ul .tree {
  padding-left: 0.1%;
  margin: 0px 0;
}


ul {
  list-style-type: none;
  list-style-position: outside;
}


</style>