import { defineStore } from 'pinia'
import * as DropBox from "../services/DropBox"






type sessionToken = {
    user: string,
    token: string
}

function storeToken(token : sessionToken){
    localStorage.setItem("token", JSON.stringify(token));
}

function getToken(): sessionToken | null {
    const token = JSON.parse(localStorage.getItem("token"));
    return token
}

function deleteToken(token: sessionToken){
    localStorage.removeItem("token");
}

async function isSessionValid(token: string): Promise<boolean>{   
    return await DropBox.checkToken(token)
}


interface State {
    user: string | void
    sessionToken: string | void
    loggedIn: boolean
}


function initalState(): State{
    return {
        user: null,
        sessionToken: null,
        loggedIn: false,
    } as State
}


// Store for user information
export const useUser = defineStore('login', 
{
    state: (): State =>  {
        return initalState();
    },
    actions: {
        async init(){
            const token = getToken();
            if (!(token == null)){
                try{
                    const valid = await isSessionValid(token?.token);
                    if(valid){
                        this.sessionToken = token.token;
                        this.user = token.user;
                        this.loggedIn = true;
                        return
                    }else{
                        this.$patch(initalState())
                        return
                    }
    
                }
                catch(error){
                    alert(error)
                    this.$patch(initalState())
                    return
    
                }
            }else{
                this.$patch(initalState())
                return
            }
        },
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
                    this.user = null;
                    this.sessionToken = null;
                    this.loggedIn = false;
                    deleteToken({user: this.user, token: this.sessionToken});
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
