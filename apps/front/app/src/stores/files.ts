import { defineStore } from 'pinia'
import DropBox from '../services/DropBox'
import {bearerHeaderAuth} from '../helpers/auth'
import {FileInfo} from '../models/Files'



interface State {
    fileList: FileInfo[]
}

export const useFiles = defineStore(
    "files",
    {
    state: (): State => 
        {
            return {
            fileList: [],
        }
    },
    actions:
    {
        async getFileList(){
            const files = await DropBox.getFiles(bearerHeaderAuth(), '*');
            this.fileList = files.files;
        },
        async transfer(sourceId: string, destination: string){
            await DropBox.transferFile(bearerHeaderAuth(), sourceId, destination)
        }
    }
})