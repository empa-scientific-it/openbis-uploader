import { defineStore } from 'pinia'
import * as DropBox from '../services/DropBox'
import {bearerHeaderAuth} from '../helpers/auth'
import {FileInfo} from '../models/Files'
import {OpenbisObjectTypes} from '../models/Tree'


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
            const files = await DropBox.getFiles(bearerHeaderAuth(), '*');
            this.fileList = files.files;
        },
        contains(id: string){
            const names = this.fileList.map(el => el.name);
            return names.includes(id);
        },
        async transfer(sourceId: string, destination: string, dataSetType: string, level: OpenbisObjectTypes){
            if(this.contains(sourceId)){
                await DropBox.transferFile(bearerHeaderAuth(), sourceId, destination, dataSetType, level);
            }else{
                throw new Error(`File not found: ${sourceId}`);
            }
        }
    }
})