

export interface TreeNode {
    identifier: string
    type: OpenbisObjectTypes | void
    code: string  | void
    perm_id: string | void
    children: TreeNode[] | void 
    properties: {}
    ancestors: string[] | void
    descendants: string[] | void
}

export const enum OpenbisObjectTypes{
    SPACE = 'SPACE',
    PROJECT = 'PROJECT',
    COLLECTION = 'COLLECTION',
    OBJECT = 'OBJECT',
    INSTANCE = 'INSTANCE'
}