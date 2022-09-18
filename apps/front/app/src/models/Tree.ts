

export interface TreeNode {
    identifier: string
    type: OpenbisObjectTypes | void
    code: string  | void
    perm_id: string | void
    children: TreeNode[] | void 
    properties: {}
}

export const enum OpenbisObjectTypes{
    SPACE = 'SPACE',
    PROJECT = 'PROJECT',
    COLLECTION = 'COLLECTION',
    OBJECT = 'OBJECT',
    INSTANCE = 'INSTANCE'
}