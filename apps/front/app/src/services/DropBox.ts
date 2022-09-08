import { findDir } from "@vue/compiler-core";
import JRPC from "./JRPC";
import { bearer } from "../helpers/utils";
const apiPath = 'data-discovery';

export default{
    async login(user:string, password:string): Promise<string> {
    
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
            Promise.reject(error);
        }

    },

    async logout(token: string): Promise<boolean> {
        const req = new Request(`${apiPath}/authorize/all/logout`, {method: 'GET', headers: bearer(token)});
        const response = await fetch(req);
        const body = await response.json();
        console.log(req);
        if (response.ok){
            console.log("ok")
            return true;
        }else{
            const error = new Error(response.statusText);
            Promise.reject(error);  
        }
    },

    async checkToken(token: string): Promise<boolean>{
        const req =  new Request(`${apiPath}/authorize/all/check?token=${encodeURIComponent(token)}`, {method: 'GET'});
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            return body
        }else{
            const error = new Error(response.statusText);
            Promise.reject(error);  
        }
    },

    async getTree(headers: HeadersInit): Promise<Object> {
        const req =  new Request(`${apiPath}/openbis/tree`, {method: 'GET', headers: headers});
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            return body
        }else{
            const error = new Error(response.statusText);
            Promise.reject(error);  
        }
    },

    async getFiles(headers: HeadersInit, pattern: string): Promise<Object> {
        const req =  new Request(`${apiPath}/datasets/`, {method: 'GET', headers: headers});
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            return body
        }else{
            const error = new Error(response.statusText);
            Promise.reject(error);  
        }
    },
    async transferFile(headers: HeadersInit, fileId: string, targetId: string): Promise<object>{
        const req =  new Request(`${apiPath}/datasets/transfer?source=${encodeURIComponent(fileId)}`, {method: 'GET', headers: headers});
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            return body
        }else{
            const error = new Error(response.statusText);
            Promise.reject(error);  
        }
    }
}