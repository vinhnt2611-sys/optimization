# # class Node:
# #     def __init__(self, val):
# #         self.val = val
# #         self.next = None  # mặc định chưa trỏ đến đâu


# # # def build(arr) :
# # #     if not arr : 
# # #         return None 
    
# # #     head = Node(arr[0])
# # #     cur = head 

# # #     for val in arr[1:] : 
# # #         cur.next = Node(val)
# # #         cur = cur.next

# # #     return head 


# # # arr = list(map(int,input().split()))
# # # head = build(arr)
# # # def length(head) : 
# # #     count = 0 
# # #     cur = head 
# # #     while cur is not None : 
# # #         count += 1 
# # #         cur = cur.next

# # #     return count 

# # # target = int(input())
# # # def search(head,target) :
# # #     count = 0 
# # #     cur = head 
# # #     while cur is not None : 
# # #         if cur.val == target : 
# # #             return count 
# # #         count += 1
# # #         cur = cur.next
        
# # #     return -1 
# # # idx = int(input())
# # # def delete(head,idx) : 
# # #     cur = head 
# # #     prev = None
# # #     if cur.val == idx : 
# # #         return cur.next
    
# # #     while cur:
# # #         if cur.val == idx:
# # #             prev.next = cur.next  # prev biết node trước, nối thẳng qua
# # #             return head
# # #         prev = cur        # ghi nhớ "tôi vừa đứng ở đây"
# # #         cur = cur.next 


# # #     return head

# # # print(delete(head,idx))
# # arr = list(map(int,input().split()))
# # def build(arr) :
# #     head = Node(arr[0])
# #     cur = head 
# #     for i in arr[1:] : 
# #         cur.next = Node(i)
# #         cur = cur.next

# #     return head
# # head = build(arr)


# # def addfirst(head,v) : 
# #     cur = head
# #     while cur is not None:
# #         if cur.key == v:
# #             return head       # đã tồn tại → bỏ qua
# #         cur = cur.next
# #     new_node = Node(v)
# #     new_node.next = head 

# #     return new_node


# # def add_after(head,u,v) : 
# #     target = None 
# #     cur = head 

# #     while cur is not None : 
# #         if cur.key == v : 
# #             target = cur 

# #         if cur.key == u : 
# #             return head
        
# #         cur = cur.next 

# #     if target is None : 
# #         return head 
    
# #     new_node = Node(u)
# #     new_node.next = target.next 
# #     target.next = new_node
# #     return head

# # def add_before(head,u,v) : 
# #     cur = head 
# #     while cur is not None : 
# #         if cur.key == u : 
# #             return head 
# #         cur = cur.next 

# #     if head.key == v : 
# #         new_node = Node(u)
# #         new_node.next = head 
# #         return new_node
    
# #     while cur.next is not None : 
# #         if cur.next.key == v : 
# #             new_node == Node(u)
# #             new_node.next == cur.next
# #             cur.next = new_node

# #             return head
        
# #         cur = cur.next 

# #     return head

# # def deletenode(head,u) : 
# #     cur = head

# #     if head.key == u : 
# #         return head.next
    
# #     while cur.next is not None : 
# #         if cur.next.key == u : 
# #             cur.next = cur.next.next
# #             return head 
# #         cur = cur.next 
# #     return head
# n = int(input())
# def paren(n) :

#     res = []
#     path = []

#     def Try(l,r) :
#         if l + r == 2*n : 
#             res.append(''.join(str(x) for x in path))
#             return 
        
#         if l < n : 
#             path.append('(')
#             Try(l+1,r)
#             path.pop()
        
#         if r < l : 
#             path.append(')')
#             Try(l,r+1)
#             path.pop()

#     Try(0,0)
#     return res 


# res = paren(n)
# print(res)

class Node:
    def __init__(self, key):
        self.key = key
        self.next = None


def build_from_list(values):
    head = None
    tail = None

    for value in values:
        new_node = Node(value)
        if head is None:
            head = new_node
            tail = new_node
        else:
            tail.next = new_node
            tail = new_node

    return head


def print_list(head):
    cur = head
    while cur is not None:
        print(cur.key, end=" ")
        cur = cur.next
    print()

def remove_node(head, target):
    #function removes the first node havin the value = target
    # return the head of obtained list 

    cur = head 
    ans = []
    while cur is not None : 
        ans.append(cur.key)
        cur = cur.next 
    
    res = []
    found = False 
    for i in ans : 
        if i == target and not found : 
            found = True 
            continue 
        res.append(i)
        
    dummy = Node(0)
    prev = dummy 

    for i in res : 
        new_node = Node(i)
        prev.next = new_node
        prev = prev.next 
        
    return dummy.next
        
        
    
def length(head):
    #return number of nodes in a singly linked list

# insert your source code here
  pass   #remove this statement in case you have your own source code for this function.
def count_value(head, target):
# return number of times the value target appears in the linked list.

# insert your source code here
  pass   #remove this statement in case you have your own source code for this function.
def solve():
    n = int(input())
    values = list(map(int, input().split()))
    head = build_from_list(values)

    while True:
        line = input().strip()
        if line == "#":
            break

        parts = line.split()
        cmd = parts[0]

        if cmd == "remove":
            k = int(parts[1])
            head = remove_node(head, k)
            print_list(head)

        elif cmd == "len":
            print(length(head))

        elif cmd == "count":
            target = int(parts[1])
            print(count_value(head, target))


solve()
