import { defineStore } from 'pinia'
import DropbBox from "../services/DropBox"
import {TreeNode} from "../models/Tree"
import {bearerHeaderAuth} from '../helpers/auth'

interface OpenbisTreeState{
    tree: TreeNode
    current: [string]
}


export const useOpenbis = defineStore('openbis', 
{
    state:  () => {
        return {
            tree: {id: '/'},
            current: '/'
        }},
    actions:
    {
        async  updateTree(){
            const tree = await DropbBox.getTree(bearerHeaderAuth());
            this.tree = tree;
        }
    }
}
)