class TreeNode():
    '''
    Clase TreeNode: representa un nodo de un arbol de expresiones regulares
    '''

    def __init__(self, val):
        self.val = val
        self.number = None
        self.nullable = False
        self.firstPos = []
        self.lastPos = []
        self.followPos = []
        self.left = None
        self.right = None

    '''
    metodo para poder imprimir el arbol de expresiones regulares
    '''

    def __str__(self):
        s = f"TreeNode: {self.val}, number: {self.number}, nullable: {self.nullable}, firstPos: {self.firstPos}, lastPos: {self.lastPos}, followPos: {self.followPos}"
        if self.left is not None:
            s += f"\n\tLeft: TreeNode: {self.left.val}, nullable: {self.left.nullable}, firstPos: {self.left.firstPos}, lastPos: {self.left.lastPos}, followPos: {self.left.followPos}"
        if self.right is not None:
            s += f"\n\tRight: TreeNode: {self.right.val}, nullable: {self.right.nullable}, firstPos: {self.right.firstPos}, lastPos: {self.right.lastPos}, followPos: {self.right.followPos}"
        return s
