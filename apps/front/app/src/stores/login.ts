import { defineStore } from 'pinia'
import * as DropBox from "../services/DropBox"






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

async function existingSession(token: sessionToken | void): Promise<boolean>{
    if (token != undefined){
        if ((token.token !== undefined)){
            return await DropBox.checkToken(token.token);
        }
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
       
        const token = getToken();
        //const exists = (async () => await existingSession(token))();
        const exists = false;
        if (exists && token != undefined){
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
                const token = await DropBox.login(user, password);
                this.user = user;
                this.sessionToken = token;
                this.loggedIn = true;
                storeToken({user, token});
                return true;
            }
            catch(err){
                console.log(err);
                return false;
            }
            
        },
        async tokenValid(): Promise<boolean>{
            const valid = await DropBox.checkToken(this.sessionToken);
            if(!valid){
                this.loggedIn = false;
            }
            return valid
        },
        async logout(): Promise<boolean>{
            try{
                const done = await DropBox.logout(this.sessionToken);
                if(done){
                    this.user = '';
                    this.sessionToken = '';
                    this.loggedIn = false;
                    deleteToken(this.sessionToken);
                    return true
                }else{
                    return false
                }
            }catch(e){
                alert(e);
            }
            
        },
        getToken(): string {
            if (this.loggedIn) {return this.sessionToken}
        }
    }
})
