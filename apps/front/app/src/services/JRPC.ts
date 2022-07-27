export default {
    rpcRequest(path: string, method: string, params: any[]) : Request {
        const req = new Request(
            path,
            {
                method: "POST",
                headers: {"Accept": "application/json"},
                body: JSON.stringify({id: 1, jsonrpc: 2, method: method, params: params})
            }
        )
        return req
    }
}
