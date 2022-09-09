import { defineStore } from 'pinia'
import DropBox from '../services/DropBox'
import {bearerHeaderAuth} from '../helpers/auth'
import {FileInfo} from '../models/Files'



interface State {
    fileList: FileInfo[],
    selected: string | void
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
        async transfer(sourceId: string, destination: string){
            if(this.contains(sourceId)){
                await DropBox.transferFile(bearerHeaderAuth(), sourceId, destination);
            }else{
                throw new Error(`File not found: ${sourceId}`);
            }
        }
    }
})