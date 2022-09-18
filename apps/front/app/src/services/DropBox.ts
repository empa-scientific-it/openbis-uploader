import { findDir } from "@vue/compiler-core";
import JRPC from "./JRPC";
import { bearer } from "../helpers/utils";
import {OpenbisObjectTypes} from '../models/Tree';
import { ParserParameters, ParserParameter } from '../models/ParserParameters'

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
    const base = `${apiPath}/authorize/all/check?`
    const params = new  URLSearchParams({token: token})
    const req =  new Request( base + params.toString(), {method: 'GET'});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body.valid
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
    

export async function uploadFile(headers: HeadersInit, file: File): Promise<object>{
    const payload = new FormData();
    payload.append('file', file, file.name);
    const req =  new Request(`${apiPath}/datasets/`, {method: 'POST', headers: headers, 'body': payload});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}

export async function  getParsers(headers: HeadersInit): Promise<string[]>{
    const req =  new Request(`${apiPath}/datasets/parsers`, {method: 'GET', headers: headers});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return body
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}

export async function  getParserParameters(headers: HeadersInit, parser: string): Promise<ParserParameters>{
    const param_string = new URLSearchParams();
    param_string.append('parser', parser);
    const req =  new Request(`${apiPath}/datasets/parser_info?` + param_string.toString(), {method: 'GET', headers: headers});
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        return (body as ParserParameters);
    }else{
        const error = new Error(response.statusText);
        throw(error);  
    }
}

export async function getProperties(headers: HeadersInit, identifier: string, type: OpenbisObjectTypes) {
    const param_string = new URLSearchParams();
    param_string.append('identifier', identifier);
    param_string.append('type', type);
    const req =  new Request(`${apiPath}/openbis/info?` + param_string.toString(), {method: 'GET', headers: headers});
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


function transferBody(fileId: string, targetId: string, datasetType: string, targetType: OpenbisObjectTypes, parser: string, parameters: object): object
{

    const a  =  {
        ...((targetType == OpenbisObjectTypes.OBJECT) ? {object: targetId} : {}),
        ...((targetType == OpenbisObjectTypes.COLLECTION) ? {collection: targetId} : {}),
        dataset_type: datasetType,
        parser: parser,
        source: fileId,
        function_parameters: parameters
        
    }
    return a
}

export async function  transferFile(headers: Headers, fileId: string, targetId: string, datasetType: string, targetType: OpenbisObjectTypes, parser: string, params: object): Promise<object>{
    const req_string = `${apiPath}/datasets/transfer` 
    const param_string = new URLSearchParams();
    if(![OpenbisObjectTypes.OBJECT, OpenbisObjectTypes.COLLECTION].includes(targetType)){
        throw new Error('Can only upload to object or collection')
    }else{
        const reqBody = transferBody(fileId, targetId, datasetType, targetType, parser, params)
        console.log(JSON.stringify(reqBody))
        headers.set('Accept', 'application/json')
        headers.set('Content-Type', 'application/json')
        const req =  new Request(req_string , {method: 'PUT', headers: headers, body: JSON.stringify(reqBody)});
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            return body
        }else{
            console.log(body)
            const error = new Error(JSON.stringify(body?.detail));
            throw(error);  
        }
    }

}