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
        const ct = {identifier: '/', type: 'INSTANCE', children: [], properties: {}, ancestors: [] as string[], descendants: [] as string[]} as TreeNode
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
        },
        async getAttributes(): Promise<void>{
            const tok = await bearerHeaderAuth();
            const attr = await DropBox.getProperties(tok, this.current.identifier, this.current.type);
            this.current.properties = attr?.properties;
        },
        async delete(tn: TreeNode){
            const tok = await bearerHeaderAuth();
            await DropBox.deleteObject(tok, tn.identifier);
            await this.updateTree();
        }

    }
}
)