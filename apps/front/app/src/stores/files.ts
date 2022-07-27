import { defineStore } from 'pinia'

interface FileInfo {
    name: String,
    path: String,
    modified: Date,
    created: Date,
    size: Number
}

interface State {
    fileList: FileInfo[],
    uploadedFiles: FileInfo[]
}

export const useFiles = defineStore(
    "files",
    {
    state: (): State => 
        {
            return {
            fileList: [],
            uploadedFiles: [],
        }
    },
    actions:
    {
        async getFileList(){
            
        }
    }
})