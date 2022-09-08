<script setup lang="ts">
import { ref, computed } from 'vue'
import { TreeNode } from '../models/Tree'
import { PropType } from 'vue';

const props = defineProps({
    model: Object as PropType<TreeNode>
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



</script>


<template>
  <li>
    <div @click="toggle">
        <i :class="itemIcon"></i>
        
        <span v-if="isFolder"><i :class="isOpen ? 'bi bi-dash-circle' : 'bi bi-plus-circle'"></i></span>
        {{ model.id }}
    </div>
    <ul v-show="isOpen" v-if="isFolder">
      <TreeItem class="item" v-for="model in model.children" :model="model">
      </TreeItem>
    </ul>
  </li>
</template>

<style>
ul {
  list-style-type: none;
}
ul li {
        margin-left:50px;
}
</style>