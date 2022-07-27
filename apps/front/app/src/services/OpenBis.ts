import JRPC from './JRPC';

const v1API = "openbis/rmi-general-information-v1.json";
const v3API = "openbis/rmi-application-server-v3.json";

export default {

    
    async checkToken(token: string): Promise<boolean>{
        const req = JRPC.rpcRequest(v1API, "isSessionActive", [token]);
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            const exists = body?.result;
            const error = body?.error;
            if (exists){
                return true
            } else{ 
                return false
            }
        } else{
            const error = new Error(response.statusText);
            Promise.reject(error);
        }
    },

    async logout(token: string){
        const req = JRPC.rpcRequest(v3API, "logout", [token]);
        const response = await fetch(req);
        if (response.ok){
            return true
        }else{
            const error = new Error(response.statusText);
            Promise.reject(error);
            return false
        }
       
    },

    async login(user:string, password:string): Promise<string> {
        const req = JRPC.rpcRequest(v3API, "login", [user, password]);
        const response = await fetch(req);
        const body = await response.json();
        if (response.ok){
            const token = body?.result
            if (token){
                return token;
            } else{
                Promise.reject(new Error("Wrong user or password"));
            }
        } else{
            const error = new Error(response.statusText);
            Promise.reject(error);
        }

    }

}

