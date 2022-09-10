

export interface TreeNode {
    id: string
    type: OpenbisObjectTypes | void
    code: string  | void
    children: TreeNode[] | void 
}

export enum OpenbisObjectTypes{
    SPACE,
    PROJECT,
    COLLECTION,
    OBJECT,
    INSTANCE
}