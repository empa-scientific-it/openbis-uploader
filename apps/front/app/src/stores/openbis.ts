import { defineStore } from 'pinia'
import DropbBox from "../services/DropBox"
import {TreeNode} from "../models/Tree"
import {bearerHeaderAuth} from '../helpers/auth'

interface OpenbisTreeState{
    tree: TreeNode
    current: TreeNode | void
    datasetTypes: string[] | void
}


export const useOpenbis = defineStore('openbis', 
{
    state:  () => {
        return {
            tree: {id: '/', type: 'INSTANCE', children: []},
            current: null,
            datasetTypes: []
        }},
    actions:
    {
        async  updateTree(){
            const tree = await DropbBox.getTree(bearerHeaderAuth());
            this.tree = tree;
        },
        async getDatasetTypes(): Promise<string[]> {
            const ds = await DropbBox.getDatasetTypes(bearerHeaderAuth());
            this.datasetTypes = ds;
            return ds
        },
        async init(): Promise<void> {
            await this.updateTree();
            await this.getDatasetTypes();
        }

    }
}
)