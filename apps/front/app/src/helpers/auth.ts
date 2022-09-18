import {useUser, existingSession} from "@/stores/login"


function bearer(token: String): HeadersInit {
    const headers: HeadersInit = new Headers();
    headers.set('Authorization', `Bearer ${token}`);
    return headers
}
    



async function bearerHeaderAuth(): Promise<HeadersInit> {
    const user = useUser();
    if(user?.sessionToken &&  await user?.tokenValid()){
        return bearer(user.sessionToken)
    }else
    {
        const headers: HeadersInit = new Headers();
        return headers
    }
}

export {bearerHeaderAuth}