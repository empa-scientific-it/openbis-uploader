<script setup lang="ts">
import { ref, computed } from 'vue'
import { TreeNode } from '../models/Tree'
import { PropType } from 'vue';

const props = defineProps({
    model: Object as PropType<TreeNode>,
    handleDrop: Function
})

const isOpen = ref(false)
const isFolder = computed(() => {
  return props.model.children && props.model.children.length
})

const itemIcon = computed(() => {
    switch(props.model.type){
        case "SPACE": return "bi bi-folder"
        case "INSTANCE": return "bi bi-folder"
        case "PROJECT": return "bi bi-folder"
        case "COLLECTION": return "bi bi-table"
        case "OBJECT": return "bi bi-card-list"
    }
    }
    );

function toggle() {
  isOpen.value = !isOpen.value
}

const emit = defineEmits<{(event: 'dropped', target: string): void }>();

function handleDrop(event){
  console.log(event.dataTransfer.getData('id'))
  console.log(`Handler Currently in ${props.model.id}`);
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
        <div @click="toggle"  @drop="handleDrop" @dragover.prevent @dragenter.prevent> 
          <div >
            inner
            <i :class="itemIcon"></i>
            <span v-if="isFolder">
              <i :class="isOpen ? 'bi bi-dash-circle' : 'bi bi-plus-circle'"></i>
            </span>
            {{ model.id }}
          </div>
        </div>
    <ul v-show="isOpen" v-if="isFolder" >
      <TreeItem class="item" v-for="model in model.children" :model="model" @dropped="handleDropped">
      </TreeItem>
    </ul>
  </li>
</template>

<style>
ul {
  list-style-type: none;
}

</style>