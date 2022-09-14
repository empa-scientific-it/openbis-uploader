import { defineStore } from 'pinia'
import * as DropBox from "../services/DropBox"
import {TreeNode} from "../models/Tree"
import { ParserParameters } from '../models/ParserParameters'
import {bearerHeaderAuth} from '../helpers/auth'

interface OpenbisTreeState{
    tree: TreeNode
    current: TreeNode | void
    datasetTypes: string[] | void
}


export const useOpenbis = defineStore('openbis', 
{
    state:  () => {
        const ct = {id: '/', type: 'INSTANCE', children: []}
        return {
            tree: ct,
            current: ct,
            datasetTypes: [] as string[],
            parserTypes: [] as string[]
        }},
    actions:
    {
        async  updateTree(){
            const tree = await DropBox.getTree(bearerHeaderAuth());
            this.tree = tree;
        },
        async getDatasetTypes(): Promise<string[]> {
            const ds = await DropBox.getDatasetTypes(bearerHeaderAuth());
            this.datasetTypes = ds;
            return ds
        },
        async getParsers(): Promise<string[]>{
            const ds = await DropBox.getParsers(bearerHeaderAuth());
            this.parserTypes = ds;
            return ds
        },
        async getParserParameters(parser: string): Promise<ParserParameters>{
            return await DropBox.getParserParameters(bearerHeaderAuth(), parser);
        },
        async init(): Promise<void> {
            await this.updateTree();
            await this.getDatasetTypes();
            await this.getParsers();
        }

    }
}
)