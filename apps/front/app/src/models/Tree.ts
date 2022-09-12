

export interface TreeNode {
    id: string
    type: OpenbisObjectTypes | void
    code: string  | void
    children: TreeNode[] | void 
}

export const enum OpenbisObjectTypes{
    SPACE = 'SPACE',
    PROJECT = 'PROJECT',
    COLLECTION = 'COLLECTION',
    OBJECT = 'OBJECT',
    INSTANCE = 'INSTANCE'
}