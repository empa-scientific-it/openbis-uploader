import { defineStore } from 'pinia'
import OpenBis from "../services/OpenBis"






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

function deleteToken(token: sessionToken){
    localStorage.removeItem("token");
}

async function existingSession(): Promise<boolean>{
    const token = getToken();
    if (token){
        return await OpenBis.checkToken(token.token);
    }
    else{
        return false;
    }
}

interface State {
    user: string
    sessionToken: string
    loggedIn: boolean
    instance: string
}

// Store for user information
export const useUser = defineStore('login', 
{
    state:  (): State =>  {
        const exists = (async () => await existingSession())();
        const token = getToken();
        if (exists && token){
            return {
                user: token.user,
                sessionToken: token.token,
                loggedIn: true,
                instance: ''
            } 
        }
        else{
            return {
                user: '',
                sessionToken: '',
                loggedIn: false,
                instance: ''
            } 
        }
    },
    actions: {
        async  login(user:string, password:string): Promise<boolean> {
            try{
                const token = await OpenBis.login(user, password);
                this.user = user;
                this.sessionToken = token;
                this.loggedIn = true;
                return true;
            }
            catch(err){
                alert(err);
            }
            
        },
        async logout(): Promise<boolean>{
            try{
                const done = await OpenBis.logout(this.sessionToken);
                if(done){
                    this.user = '';
                    this.sessionToken = '';
                    this.loggedIn = false;
                    return true
                }else{
                    return false
                }
            }catch(e){
                alert(e);
            }
            
        }
    }
})
