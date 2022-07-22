import { defineStore } from 'pinia'


function combineUserPassword(user: string, password: string){
    return `"${user}", "${password}"`
}

async function checkToken(token: string): Promise<boolean>{
    const req = new Request(
        "openbis/rmi-general-information-v1.json",
        {
            method: 'POST',
            headers: {"Accept": "application/json"},
            body: JSON.stringify({id: 1, jsonrpc: 2, method: "isSessionActive", params: [token]})
        },
    );
    const response = await fetch(req);
    const body = await response.json();
    if (response.ok){
        const exists = body?.result
        const error = body?.error
        if (exists){
            return true
        } else{ 
            return false
        }
    } else{
        const error = new Error(response.statusText)
        Promise.reject(error)
    }
}

type sessionToken = {
    user: string,
    token: string
}

function storeToken(token : sessionToken){
    localStorage.setItem("token", JSON.stringify(token));
}

function getToken(): sessionToken | void {
    const token = JSON.parse(localStorage.getItem("token"));
    return token
}

async function existingSession(): Promise<boolean>{
    const token = getToken();
    if (token){
        return await checkToken(token.token);
    }
    else{
        return false;
    }
}

// Store for user information
export const useUser = defineStore('login', 
{
    state:  () =>  {
        const exists = (async () => await existingSession())();
        const token = getToken();
        if (exists && token){
            return {
                user: token.user,
                sessionToken: token.token,
                loggedIn: true
            }
        }
        else{
            return {
                user: '',
                sessionToken: '',
                loggedIn: false
            }
        }
    },
    actions: {
        async  login(user:string, password:string): Promise<boolean> {
            const req = new Request(
                "openbis/rmi-general-information-v1.json",
                {
                    method: 'POST',
                    headers: {"Accept": "application/json"},
                    body: JSON.stringify({id: 1, jsonrpc: 2, method: "tryToAuthenticateForAllServices", params: [user, password]})
                },
            );
            const response = await fetch(req);
            const body = await response.json();
            if (response.ok){
                const token = body?.result
                if (token){
                    this.sessionToken = token;
                    this.loggedIn = true;
                    this.user = user;
                    // Push token in local storage to persist the session
                    storeToken({user:user, token: token});
                    return true;
                } else{
                    Promise.reject(new Error("Wrong user or password"))
                }
            } else{
                const error = new Error(response.statusText)
                Promise.reject(error)
            }

        }
    }
})
