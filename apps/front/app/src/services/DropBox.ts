import JRPC from "./JRPC";
const apiPath = 'data-discovery';

export default{
    async listFiles(){
        Request(
            `{apiPath}/`
        )
    }
}