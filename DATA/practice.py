
def bubble_sort(arr):
    n = len(arr)
    
    for i in range(n -1 , 2, -1):
        for j in range(i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1]= arr[j+1], arr[j]
            print(arr)
        print(f"for {i} finished")
# arr = [4,6,2,8,4,9,1,54,85,32,68]
# bubble_sort(arr)


def insertion_sort(arr):
    arr = [float('-inf')] + arr
    n = len(arr)
    for i in range(1, n):
        temp = arr[i]
        print(temp)
        j = i -1 
        print(arr[j])
        while arr[j] >= temp:
            arr[j+1] = arr[j]
            print(arr)
            j -=1
        arr[j+ 1] = temp
        print('After the while loop: ',arr)
    return arr
arr = [5,3,6,1,2,4,8,7]
# print("Final ",insertion_sort(arr))


def selection_sort(arr):
	n = len(arr)
	for i in range(n-1,0,-1):
		k = 0
		for j in range(1,i+1):
			if arr[j]>arr[k]:
				k = j
		arr[k], arr[i] = arr[i], arr[k]
	return arr


print("Final ",selection_sort(arr))
