export interface ParserParameter{
    title: string
    type: string
}

export interface ParserParameters{
    title: string,
    type: string,
    properties: Map<string, ParserParameter>
    required: Array<string>
}


export interface ParserParametersResponse{

}

export function parameterObject(pp: ParserParameters): Map<string, any> {
    const res = [...new Map(Object.entries(pp?.properties))].map(([k, v]) => [k, null])
    return Object.fromEntries(res)
}