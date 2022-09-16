
function bearer(token: String): HeadersInit {
    const headers: HeadersInit = new Headers();
    headers.set('Authorization', `Bearer ${token}`);
    return headers
}
    


export {bearer}