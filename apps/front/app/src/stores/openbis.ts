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
        const ct = {identifier: '/', type: 'INSTANCE', children: []} as TreeNode
        return {
            tree: ct,
            current: ct,
            datasetTypes: [] as string[],
            parserTypes: [] as string[]
        }},
    actions:
    {
        async  updateTree(){
            const tok = await bearerHeaderAuth()
            const tree = await DropBox.getTree(tok);
            this.tree = tree;
        },
        async getDatasetTypes(): Promise<string[]> {
            const tok = await bearerHeaderAuth()
            const ds = await DropBox.getDatasetTypes(tok);
            this.datasetTypes = ds;
            return ds
        },
        async getParsers(): Promise<string[]>{
            const tok = await bearerHeaderAuth()
            const ds = await DropBox.getParsers(tok);
            this.parserTypes = ds;
            return ds
        },
        async getParserParameters(parser: string): Promise<ParserParameters>{
            const tok = await bearerHeaderAuth()
            return await DropBox.getParserParameters(tok, parser);
        },
        async init(): Promise<void> {
            await this.updateTree();
            await this.getDatasetTypes();
            await this.getParsers();
        }

    }
}
)