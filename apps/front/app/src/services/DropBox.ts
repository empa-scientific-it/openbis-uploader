import { findDir } from "@vue/compiler-core";
import JRPC from "./JRPC";
import { bearer } from "../helpers/utils";
import {OpenbisObjectTypes} from '../models/Tree';

const apiPath = 'data-discovery';

export async function login(user:string, password:string): Promise<string> {

    const fd =  new FormData();
    fd.append("username", user);
    fd.append("password", password);
    const req = new Request(`${apiPath}/authorize/all/token`, {method: 'POST', body: fd});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){   
        console.log(body?.access_token)
        const token = body?.access_token
        if (token !== null){
            return token;
        } else{
            Promise.reject(new Error("Wrong user or password"));
        }
    } else {
        const error = new Error(response.statusText);
        throw(error);
    }

}

export async function logout(token: string): Promise<boolean> {
    const req = new Request(`${apiPath}/authorize/all/logout`, {method: 'GET', headers: bearer(token)});
    const response = await fetch(req);
    const body = await response.json();
    console.log(req);
    if (response.ok){
        console.log("ok")
        return true;
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}

export async function  checkToken(token: string): Promise<boolean>{
    const base = `${apiPath}/authorize/all/check?token`
    const params = new  URLSearchParams({token: token})
    const req =  new Request( base + params.toString(), {method: 'GET'});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}

export async function  getTree(headers: HeadersInit): Promise<Object> {
    const req =  new Request(`${apiPath}/openbis/tree`, {method: 'GET', headers: headers});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}

export async function  getDatasetTypes(headers: HeadersInit): Promise<string[]>{
        const req =  new Request(`${apiPath}/openbis/dataset_types`, {method: 'GET', headers: headers});
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            return body
        }else{
            const error = new Error(response.statusText);
            throw(error);  
        }
}
    
export async function  getFiles(headers: HeadersInit, pattern: string): Promise<Object> {
    const req =  new Request(`${apiPath}/datasets/`, {method: 'GET', headers: headers});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}
export async function  transferFile(headers: HeadersInit, fileId: string, targetId: string, datasetType: string, targetType: OpenbisObjectTypes): Promise<object>{
    const req_string = `${apiPath}/datasets/transfer?` 
    const param_string = new URLSearchParams();
    switch(targetType){
        case OpenbisObjectTypes.SPACE:
            console.log("SPACE")
            throw new Error("Cannot assign dataset to spaces");
        case OpenbisObjectTypes.INSTANCE:
            console.log("INSTANCE")
            throw new Error("Cannot assign dataset to instance");
        case OpenbisObjectTypes.PROJECT:
            throw new Error("Cannot assign dataset to projects");
        case OpenbisObjectTypes.OBJECT:
            console.log("OBJECT")
            param_string.append("object", targetId);
            break;
        case OpenbisObjectTypes.COLLECTION:
            param_string.append("collection", targetId)
            console.log("COllection")
            break;
    }
    param_string.append('dataset_type', datasetType);
    param_string.append('source', fileId);
    console.log(param_string);
    const req =  new Request(req_string + param_string.toString(), {method: 'GET', headers: headers});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body
    }else{
        const error = new Error(JSON.stringify(body?.detail));
        throw(error);  
    }
}