import { defineStore } from 'pinia'
import * as DropBox from '../services/DropBox'
import {bearerHeaderAuth} from '../helpers/auth'
import {FileInfo} from '../models/Files'
import {OpenbisObjectTypes} from '../models/Tree'
import { ParserParameters } from '../models/ParserParameters'



interface State {
    fileList: FileInfo[],
    selected: FileInfo | void
}

export const useFiles = defineStore(
    "files",
    {
    state: (): State => 
        {
            return {
            fileList: [],
            selected:  null
        }
    },
    actions:
    {
        async getFileList(){
            const tok = await bearerHeaderAuth();
            const files = await DropBox.getFiles(tok, '*');
            this.fileList = files.files;
        },
        contains(id: string){
            const names = this.fileList.map(el => el.name);
            return names.includes(id);
        },
        async uploadFile(file: File){
            const tok = await bearerHeaderAuth();
            await DropBox.uploadFile(tok, file);
            await this.getFileList();
        },
        async transfer(sourceId: string, destination: string, dataSetType: string, level: OpenbisObjectTypes, parser: string, params: ParserParameters){
            if(this.contains(sourceId)){
                const tok = await bearerHeaderAuth();
                await DropBox.transferFile(tok, sourceId, destination, dataSetType, level, parser, params);
            }else{
                throw new Error(`File not found: ${sourceId}`);
            }
        }
    }
})